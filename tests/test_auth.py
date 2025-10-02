import os
from unittest import TestCase
from unittest.mock import patch, Mock

import requests

from d2spy.auth import Auth
from example_data import TEST_USER


class TestAuth(TestCase):
    @patch("d2spy.auth.requests.get")
    def test_auth_init_with_valid_url(self, mock_get):
        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create an Auth instance with a valid D2S URL
        base_url = "https://valid-d2s-url.org"
        auth = Auth(base_url)

        # Assert that the correct URL was used to validate the base url
        mock_get.assert_called_once_with(f"{base_url}/api/v1/health")

        # Assert that the Auth instance returned a requests session
        self.assertIsInstance(auth.session, requests.Session)

    @patch("d2spy.auth.requests.get")
    def test_auth_init_with_invalid_url(self, mock_get):
        # Create a mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Create an Auth instance with a invalid D2S URL
        with self.assertRaises(ValueError) as context:
            base_url = "https://invalid-d2s-url.org"
            Auth(base_url)

        # Assert that the correct exception text was returned
        self.assertEqual(str(context.exception), "unable to connect to provided host")

        # Assert that the correct URL was used to validate the base url
        mock_get.assert_called_once_with(f"{base_url}/api/v1/health")

    @patch("d2spy.auth.requests.get")
    @patch("getpass.getpass")
    @patch("d2spy.auth.requests.post")
    @patch("d2spy.auth.requests.Session.get")
    @patch.dict("os.environ", {}, clear=True)
    def test_login_and_get_current_user(
        self, mock_get_login, mock_post, mock_getpass, mock_get_init
    ):
        # Valid D2S URL
        base_url = "https://valid-d2s-url.org"

        # Mock the GET request that occurs when Auth is initialized
        mock_get_init_response = Mock()
        mock_get_init_response.status_code = 200
        mock_get_init.return_value = mock_get_init_response

        # Mock the POST request that occurs during login
        mock_post_response = Mock()
        mock_post_response.cookies = {
            "access_token": "fake_token",
            "refresh_token": "fake_refresh_token",
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # User email addressed used during login
        user_email = "user@example.com"
        # Mock user password
        user_password = "userpassword"
        mock_getpass.return_value = user_password

        # Mock the GET request that occurs after login
        mock_get_login_response = Mock()
        mock_get_login_response_data = {
            "email": user_email,
            "first_name": "string",
            "last_name": "string",
            "is_email_confirmed": True,
            "is_approved": True,
            "id": "uuid-string",
            "created_at": "2024-08-29T13:49:55.191Z",
            "api_access_token": "abc123",
            "exts": [],
            "is_superuser": False,
            "profile_url": "https://example.com",
        }
        mock_get_login_response.status_code = 200
        mock_get_login_response.json.return_value = mock_get_login_response_data
        mock_get_login.return_value = mock_get_login_response

        # Create an Auth instance and login
        auth = Auth(base_url)
        login_session = auth.login(email=user_email)

        # Assert that the correct URLs were called
        mock_get_init.assert_called_once_with(f"{base_url}/api/v1/health")
        mock_post.assert_called_once_with(
            f"{base_url}/api/v1/auth/access-token",
            data={"username": user_email, "password": user_password},
        )
        mock_get_login.assert_called_once_with(f"{base_url}/api/v1/users/current")

        # Assert login returns session with access_token and refresh_token in cookies
        self.assertIsInstance(login_session, requests.Session)
        self.assertTrue(hasattr(login_session, "d2s_data"))
        self.assertIn("API_KEY", login_session.d2s_data)
        self.assertEqual(
            login_session.d2s_data["API_KEY"],
            mock_get_login_response_data["api_access_token"],
        )
        self.assertIn("access_token", login_session.cookies)
        self.assertEqual(
            login_session.cookies["access_token"],
            mock_post_response.cookies["access_token"],
        )
        self.assertIn("refresh_token", login_session.cookies)
        self.assertEqual(
            login_session.cookies["refresh_token"],
            mock_post_response.cookies["refresh_token"],
        )

    @patch("d2spy.auth.requests.get")
    @patch("getpass.getpass")
    @patch("d2spy.auth.requests.post")
    @patch("d2spy.auth.requests.Session.get")
    def test_login_with_environment_variables_and_get_current_user(
        self, mock_get_login, mock_post, mock_getpass, mock_get_init
    ):
        # Valid D2S URL
        base_url = "https://valid-d2s-url.org"

        # Mock the GET request that occurs when Auth is initialized
        mock_get_init_response = Mock()
        mock_get_init_response.status_code = 200
        mock_get_init.return_value = mock_get_init_response

        # Mock the POST request that occurs during login
        mock_post_response = Mock()
        mock_post_response.cookies = {
            "access_token": "fake_token",
            "refresh_token": "fake_refresh_token",
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Set email and password as environment variables
        os.environ["D2S_EMAIL"] = "user@example.com"
        os.environ["D2S_PASSWORD"] = "userpassword"

        # Mock the GET request that occurs after login
        mock_get_login_response = Mock()
        mock_get_login_response_data = {
            "email": os.environ.get("D2S_EMAIL"),
            "first_name": "string",
            "last_name": "string",
            "is_email_confirmed": True,
            "is_approved": True,
            "id": "uuid-string",
            "created_at": "2024-08-29T13:49:55.191Z",
            "api_access_token": "abc123",
            "exts": [],
            "is_superuser": False,
            "profile_url": "https://example.com",
        }
        mock_get_login_response.status_code = 200
        mock_get_login_response.json.return_value = mock_get_login_response_data
        mock_get_login.return_value = mock_get_login_response

        # Create an Auth instance and login
        auth = Auth(base_url)
        login_session = auth.login()

        # Assert that the correct URLs were called
        mock_get_init.assert_called_once_with(f"{base_url}/api/v1/health")
        mock_post.assert_called_once_with(
            f"{base_url}/api/v1/auth/access-token",
            data={
                "username": os.environ.get("D2S_EMAIL"),
                "password": os.environ.get("D2S_PASSWORD"),
            },
        )
        mock_get_login.assert_called_once_with(f"{base_url}/api/v1/users/current")

        # Assert login returns session with access_token and refresh_token in cookies
        self.assertIsInstance(login_session, requests.Session)
        self.assertTrue(hasattr(login_session, "d2s_data"))
        self.assertIn("API_KEY", login_session.d2s_data)
        self.assertEqual(
            login_session.d2s_data["API_KEY"],
            mock_get_login_response_data["api_access_token"],
        )
        self.assertIn("access_token", login_session.cookies)
        self.assertEqual(
            login_session.cookies["access_token"],
            mock_post_response.cookies["access_token"],
        )
        self.assertIn("refresh_token", login_session.cookies)
        self.assertEqual(
            login_session.cookies["refresh_token"],
            mock_post_response.cookies["refresh_token"],
        )

    @patch("d2spy.auth.requests.get")
    @patch("getpass.getpass")
    @patch("d2spy.auth.requests.post")
    @patch("d2spy.auth.requests.Session.get")
    @patch.dict("os.environ", {}, clear=True)
    def test_logout(self, mock_get_login, mock_post, mock_getpass, mock_get_init):
        # Valid D2S URL
        base_url = "https://valid-d2s-url.org"

        # Mock the GET request that occurs when Auth is initialized
        mock_get_init_response = Mock()
        mock_get_init_response.status_code = 200
        mock_get_init.return_value = mock_get_init_response

        # Mock the POST request that occurs during login
        mock_post_response = Mock()
        mock_post_response.cookies = {
            "access_token": "fake_token",
            "refresh_token": "fake_refresh_token",
        }
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # User email addressed used during login
        user_email = "user@example.com"
        # Mock user password
        user_password = "userpassword"
        mock_getpass.return_value = user_password

        # Mock the GET request that occurs after login
        mock_get_login_response = Mock()
        mock_get_login_response.status_code = 200
        mock_get_login_response.json.return_value = TEST_USER
        mock_get_login.return_value = mock_get_login_response

        # Create an Auth instance and login
        auth = Auth(base_url)
        session = auth.login(email=user_email)

        # Assert access token and refresh token are in session after login
        self.assertIn("access_token", session.cookies)
        self.assertIn("refresh_token", session.cookies)

        # Keep track of cookies to clear
        cleared_cookies = []

        # Mock the cookie jar clear method to track what gets cleared
        session.cookies.clear

        def mock_clear(domain=None, path=None, name=None):
            if name:
                cleared_cookies.append(name)
                # Find and remove the actual cookie from the jar
                for cookie in list(session.cookies):
                    if cookie.name == name:
                        session.cookies._cookies[cookie.domain][cookie.path].pop(
                            name, None
                        )

        session.cookies.clear = mock_clear
        session.close = Mock()

        # Logout of session
        auth.logout()

        # Assert that session.close was called
        session.close.assert_called_once()

        # Assert that clear was called for both tokens
        self.assertIn("access_token", cleared_cookies)
        self.assertIn("refresh_token", cleared_cookies)

        # Assert both tokens are no longer in session after logout
        self.assertNotIn("access_token", session.cookies)
        self.assertNotIn("refresh_token", session.cookies)

    @patch("d2spy.auth.requests.get")
    @patch("getpass.getpass")
    @patch("d2spy.auth.requests.post")
    @patch("d2spy.auth.requests.Session.get")
    @patch.dict("os.environ", {}, clear=True)
    def test_login_backward_compatibility_no_refresh_token(
        self, mock_get_login, mock_post, mock_getpass, mock_get_init
    ):
        """Test that login still works when backend doesn't return refresh_token
        (backward compatibility)."""
        # Valid D2S URL
        base_url = "https://valid-d2s-url.org"

        # Mock the GET request that occurs when Auth is initialized
        mock_get_init_response = Mock()
        mock_get_init_response.status_code = 200
        mock_get_init.return_value = mock_get_init_response

        # Mock the POST request that occurs during login - NO refresh_token
        mock_post_response = Mock()
        mock_post_response.cookies = {"access_token": "fake_token"}  # Only access_token
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # User email addressed used during login
        user_email = "user@example.com"
        # Mock user password
        user_password = "userpassword"
        mock_getpass.return_value = user_password

        # Mock the GET request that occurs after login
        mock_get_login_response = Mock()
        mock_get_login_response_data = {
            "email": user_email,
            "first_name": "string",
            "last_name": "string",
            "is_email_confirmed": True,
            "is_approved": True,
            "id": "uuid-string",
            "created_at": "2024-08-29T13:49:55.191Z",
            "api_access_token": "abc123",
            "exts": [],
            "is_superuser": False,
            "profile_url": "https://example.com",
        }
        mock_get_login_response.status_code = 200
        mock_get_login_response.json.return_value = mock_get_login_response_data
        mock_get_login.return_value = mock_get_login_response

        # Create an Auth instance and login
        auth = Auth(base_url)
        login_session = auth.login(email=user_email)

        # Assert that login still works without refresh_token
        self.assertIsInstance(login_session, requests.Session)
        self.assertIn("access_token", login_session.cookies)
        self.assertEqual(
            login_session.cookies["access_token"],
            mock_post_response.cookies["access_token"],
        )
        # Assert refresh_token is not present (backward compatibility)
        self.assertNotIn("refresh_token", login_session.cookies)
