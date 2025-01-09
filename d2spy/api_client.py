from typing import Any, Dict, List, Union

from requests import Session

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

        # Check if access token in session cookies
        if not self.session.cookies.get("access_token"):
            raise ValueError("Session missing access token. Must sign in first.")

    def make_get_request(
        self, endpoint: str, **kwargs
    ) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
        """Makes GET request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Union[Dict, List]: JSON response from request.
        """
        url = self.base_url + endpoint
        response = self.session.get(url, **kwargs)

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
        url = self.base_url + endpoint
        response = self.session.post(url, **kwargs)

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
        url = self.base_url + endpoint
        response = self.session.put(url, **kwargs)

        if response.status_code != 200:
            pretty_print_response(response)
            response.raise_for_status()

        return response.json()
