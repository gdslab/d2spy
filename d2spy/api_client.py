from typing import Dict, List, Union

from requests import Response, Session

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

    def make_get_request(self, endpoint: str, **kwargs) -> Union[Dict, List]:
        """Makes GET request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Union[Dict, List]: JSON response from request.
        """
        url = self.base_url + endpoint
        response = self.session.get(url, **kwargs)

        if response.status_code == 200:
            return response.json()
        else:
            pretty_print_response(response)
            response.raise_for_status()

    def make_post_request(self, endpoint: str, **kwargs) -> Union[Dict, List]:
        """Make POST request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Union[Dict, List]: JSON response from request.
        """
        url = self.base_url + endpoint
        response = self.session.post(url, **kwargs)
        print(response)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            pretty_print_response(response)
            response.raise_for_status()

    def make_put_request(self, endpoint: str, **kwargs) -> Union[Dict, List]:
        """Make PUT request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            Union[Dict, List]: JSON response from request.
        """
        url = self.base_url + endpoint
        response = self.session.put(url, **kwargs)

        if response.status_code == 200:
            return response.json()
        else:
            pretty_print_response(response)
            response.raise_for_status()
