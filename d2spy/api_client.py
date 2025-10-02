import threading
from typing import Any, Dict, List, Union
from urllib.parse import urlparse

from requests import Session, Response

from d2spy.extras.utils import pretty_print_response


class APIClient:
    """Makes API requests to D2S API."""

    def __init__(self, base_url: str, session: Session):
        """Constructor for APIClient class.

        Args:
            base_url (str): Base URL for D2S instance.
            session (Session): Session set by Auth.

        Raises:
            ValueError: Raised if access token missing from session.
        """
        self.base_url = base_url
        self.session = session
        self._is_refreshing = False
        self._refresh_lock = threading.Lock()

        # Check if access token in session cookies (avoid ambiguous .get())
        if not any(cookie.name == "access_token" for cookie in self.session.cookies):
            raise ValueError("Session missing access token. Must sign in first.")

    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token.

        Returns:
            bool: True if refresh successful, False otherwise.
        """
        # Ensure a refresh_token exists (avoid ambiguous .get())
        if not any(cookie.name == "refresh_token" for cookie in self.session.cookies):
            return False

        url = f"{self.base_url}/api/v1/auth/refresh-token"
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                # Normalize cookies to be scoped to the API host to avoid duplicates
                host = urlparse(self.base_url).hostname or ""
                if "access_token" in response.cookies:
                    # Don't set explicit domain for localhost to
                    # avoid port-matching issues
                    if host == "localhost" or host == "127.0.0.1":
                        self.session.cookies.set(
                            "access_token",
                            response.cookies["access_token"],
                            path="/",
                        )
                    else:
                        self.session.cookies.set(
                            "access_token",
                            response.cookies["access_token"],
                            domain=host,
                            path="/",
                        )
                if "refresh_token" in response.cookies:
                    # Don't set explicit domain for localhost to avoid
                    # port-matching issues
                    if host == "localhost" or host == "127.0.0.1":
                        self.session.cookies.set(
                            "refresh_token",
                            response.cookies["refresh_token"],
                            path="/",
                        )
                    else:
                        self.session.cookies.set(
                            "refresh_token",
                            response.cookies["refresh_token"],
                            domain=host,
                            path="/",
                        )
                return True
            else:
                return False
        except Exception:
            return False

    def _make_request_with_retry(
        self, method: str, endpoint: str, **kwargs
    ) -> Response:
        """Make request with automatic token refresh on 401 errors.

        Args:
            method (str): HTTP method (GET, POST, PUT, etc.)
            endpoint (str): D2S endpoint for request.
            **kwargs: Additional arguments for the request.

        Returns:
            Response: The response object.

        Raises:
            Exception: If token refresh fails or request fails after retry.
        """
        url = self.base_url + endpoint

        # Extract _retry flag and remove it from kwargs before making request
        is_retry = kwargs.pop("_retry", False)

        # Make the initial request
        response = getattr(self.session, method.lower())(url, **kwargs)

        # If we get a 401 and it's not the refresh endpoint, try to refresh
        if (
            response.status_code == 401
            and endpoint != "/api/v1/auth/refresh-token"
            and not is_retry
        ):

            with self._refresh_lock:
                if not self._is_refreshing:
                    self._is_refreshing = True
                    try:
                        # Attempt to refresh the token
                        if self._refresh_access_token():
                            # Retry the original request
                            kwargs["_retry"] = True
                            response = self._make_request_with_retry(
                                method, endpoint, **kwargs
                            )
                        else:
                            # Refresh failed, clear session
                            self.session.cookies.clear()
                            raise ValueError(
                                "Session expired and refresh failed. "
                                "Please login again."
                            )
                    finally:
                        self._is_refreshing = False
                else:
                    # Another thread is already refreshing, wait and retry once
                    import time

                    time.sleep(0.1)
                    kwargs["_retry"] = True
                    response = self._make_request_with_retry(method, endpoint, **kwargs)

        return response

    def make_get_request(
        self, endpoint: str, **kwargs
    ) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
        """Makes GET request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Union[Dict, List]: JSON response from request.
        """
        response = self._make_request_with_retry("GET", endpoint, **kwargs)

        if response.status_code != 200:
            pretty_print_response(response)
            response.raise_for_status()

        return response.json()

    def make_post_request(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make POST request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Dict: JSON response from request.
        """
        response = self._make_request_with_retry("POST", endpoint, **kwargs)

        if (
            response.status_code != 200
            and response.status_code != 201
            and response.status_code != 202
        ):
            pretty_print_response(response)
            response.raise_for_status()

        if response.status_code == 202:
            return {"status": "accepted"}

        return response.json()

    def make_put_request(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make PUT request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Dict: JSON response from request.
        """
        response = self._make_request_with_retry("PUT", endpoint, **kwargs)

        if response.status_code != 200:
            pretty_print_response(response)
            response.raise_for_status()

        return response.json()
