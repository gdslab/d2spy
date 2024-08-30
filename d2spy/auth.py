import getpass
import requests
from typing import Optional

from d2spy.extras.utils import pretty_print_response
from d2spy.models.user import User
from d2spy.schemas.session import D2SpySession


class Auth:
    """Authenticates with D2S."""

    def __init__(self, base_url: str) -> None:
        """Constructor for Auth class.

        Args:
            base_url (str): Base URL for D2S instance.

        Raises:
            ValueError: Raised if unable to communicate with host.
        """
        self.base_url: str = base_url

        if is_valid_base_url(self.base_url) is False:
            raise ValueError("unable to connect to provided host")

        self.session: D2SpySession = D2SpySession()

    def login(
        self, email: str, password: Optional[str] = None
    ) -> Optional[D2SpySession]:
        """Login to D2S platform with email and password.

        Args:
            email (str): Email address used to sign in to D2S.
            password Optional[str]: Password used to sign in to D2S.

        Returns:
            Optional[D2SpySession]: Session with user access cookie.
        """
        # Request password from user if not provided to login method
        if not password:
            password = getpass.getpass(prompt="Enter your D2S password:")
        # Credentials that will be sent to D2S auth API
        credentials = {"username": email, "password": password}
        # URL for D2S access-token endpoint
        url = f"{self.base_url}/api/v1/auth/access-token"
        # Post credentials to access-token endpoint
        response = requests.post(url, data=credentials)
        # JWT access token returned for successful request
        if response.status_code == 200 and "access_token" in response.cookies:
            # Add JWT access token to session cookies
            self.session.cookies.set("access_token", response.cookies["access_token"])
            # Fetch user object associated with access token
            user = self.get_current_user()
            # Return dictionary of user attributes and values
            if user:
                # Check if user has api key and set it to session header if so
                if hasattr(user, "api_access_token") and user.api_access_token:
                    self.session.d2s_data = {"API_KEY": user.api_access_token}
                return self.session
            else:
                return None
        else:
            # Print response if request fails
            pretty_print_response(response)
            return None

    def logout(self) -> None:
        """Logout of D2S platform."""
        # Delete access-token cookie from session and end session
        self.session.cookies.clear(domain="", path="/", name="access_token")
        self.session.close()
        print("session ended")

    def get_current_user(self) -> Optional[User]:
        """Get user object for logged in user.

        Returns:
            Optional[User]: User object or None.
        """
        # D2S endpoint for fetching user object for signed in user
        url = f"{self.base_url}/api/v1/users/current"
        # Request user object from D2S instance
        response = self.session.get(url)
        # Return user object if request successful
        if response.status_code == 200:
            return User.from_dict(response.json())
        else:
            # Print response if request fails
            pretty_print_response(response)
            return None


def is_valid_base_url(base_url: str) -> bool:
    """Return true if base_url returns HTTP 200 else false.

    Args:
        base_url (str): Base URL for D2S instance.

    Returns:
        bool: Returns True if D2S instance returns status OK, otherwise False
    """
    response: Optional[requests.Response] = None
    try:
        response = requests.get(f"{base_url}/api/v1/health")
    except requests.exceptions.ConnectionError:
        response = None
    finally:
        if response and response.status_code == 200:
            return True
    return False
