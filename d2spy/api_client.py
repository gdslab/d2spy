import requests


class APIClient:
    """Makes API requests to D2S API."""

    def __init__(self, base_url: str, session: requests.Session):
        """Constructor for APIClient class.

        Args:
            base_url (str): Base URL for D2S instance.
            session (requests.Session): Session set by Auth.

        Raises:
            ValueError: Raised if access token missing from session.
        """
        self.base_url = base_url
        self.session = session

        # Check if access token in session cookies
        if not self.session.cookies.get("access_token"):
            raise ValueError("Session missing access token. Must sign in first.")

    def make_get_request(self, endpoint: str) -> requests.Response:
        """Makes GET request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            requests.Response: Response from D2S API to request.
        """
        url = self.base_url + endpoint
        response = self.session.get(url)

        return response

    def make_post_request(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request to D2S API.

        Args:
            endpoint (str): D2S endpoint for request.

        Returns:
            requests.Response: Response from D2S API to request.
        """
        url = self.base_url + endpoint
        response = self.session.post(url, **kwargs)

        return response

    def make_put_request(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request to D2S API.

        Args:
            endpoint (str): _description_

        Returns:
            requests.Response: _description_
        """
        url = self.base_url + endpoint
        response = self.session.put(url, **kwargs)

        return response
