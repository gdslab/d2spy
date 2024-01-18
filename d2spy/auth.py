import json
import requests
from requests import exceptions, Response, Session
from typing import Union
from urllib.parse import urlparse

from .extras.utils import pretty_print_response
from .models.user import User


class Auth:
    """Authentication for D2S platform."""

    def __init__(self, email: str, password: str, host: str) -> None:
        self.email: str = email
        self.password: str = password
        self.host: str = host

        if test_host(self.host) is False:
            raise ValueError("unable to connect to provided host")

        self.session: Session = requests.session()

    def login(self) -> Union[User, None]:
        """Login to D2S platform with email and password."""
        user_credentials = {"username": self.email, "password": self.password}

        url = f"{self.host}/api/v1/auth/access-token"

        response = requests.post(url, data=user_credentials)

        if response.status_code == 200 and "access_token" in response.cookies:
            self.session.cookies.set(
                "access_token", response.cookies.get("access_token")
            )
            user = self.get_current_user()
            if user:
                return User.from_dict(user)
            else:
                return None
        else:
            pretty_print_response(response)
            return None

    def logout(self) -> None:
        """Logout of D2S platform."""
        self.session.cookies.clear(name="access_token")
        self.session.close()
        print("session ended")

    def get_current_user(self) -> Union[User, None]:
        """Get user object for logged in user."""
        url = f"{self.host}/api/v1/users/current"

        response = self.session.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            pretty_print_response(response)
            return None


def test_host(host: str) -> bool:
    """Return true if host returns HTTP 200 else false."""
    response = None
    try:
        response = requests.get(host)
    except exceptions.ConnectionError:
        response = None
    finally:
        if response and response.status_code == 200:
            return True
    return False
