from unittest import TestCase
from unittest.mock import patch, Mock
import threading

from d2spy.api_client import APIClient


class TestAPIClient(TestCase):
    @patch("requests.Session")
    def test_make_get_request(self, MockSession):
        # Create a mock JSON response
        mock_response = Mock()
        expected_result = {"status": "healthy"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_result

        # Create a mock session that returns the mock response for GET requests
        mock_session = MockSession()
        mock_session.get.return_value = mock_response

        # Instantiate the APIClient with a test URL and the mock session
        client = APIClient("http://example.com", mock_session)

        # Make a GET request to the D2S health check URL
        result = client.make_get_request("/api/v1/health")

        # Assert that the correct URL was used in the session's GET request
        mock_session.get.assert_called_once_with("http://example.com/api/v1/health")

        # Assert that the GET request method returned the expected result
        self.assertEqual(result, expected_result)

    @patch("requests.Session")
    def test_make_post_request(self, MockSession):
        # Create a mock JSON response
        mock_response = Mock()
        expected_result = {"title": "Title", "description": "Description"}
        mock_response.status_code = 201
        mock_response.json.return_value = expected_result

        # Create a mock session that returns the mock response for POST requests
        mock_session = MockSession()
        mock_session.post.return_value = mock_response

        # Instantiate the APIClient with a test URL and the mock session
        client = APIClient("http://example.com", mock_session)

        # Make a POST request to the D2S team creation URL
        result = client.make_post_request("/api/v1/teams")

        # Assert that the correct URL was used in the session's POST request
        mock_session.post.assert_called_once_with("http://example.com/api/v1/teams")

        # Assert that the POST request method returned the expected result
        self.assertEqual(result, expected_result)

    @patch("requests.Session")
    def test_make_put_request(self, MockSession):
        # Create a mock JSON response
        mock_response = Mock()
        expected_result = {"title": "Updated Title", "description": "Description"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_result

        # Create a mock session that returns the mock response for PUT requests
        mock_session = MockSession()
        mock_session.put.return_value = mock_response

        # Instantiate the APIClient with a test URL and the mock session
        client = APIClient("http://example.com", mock_session)

        # Make a PUT request to the D2S team creation URL
        result = client.make_put_request("/api/v1/teams/1")

        # Assert that the correct URL was used in the session's PUT request
        mock_session.put.assert_called_once_with("http://example.com/api/v1/teams/1")

        # Assert that the PUT request method returned the expected result
        self.assertEqual(result, expected_result)

    @patch("requests.Session")
    def test_token_refresh_on_401_success(self, MockSession):
        """Test that 401 error triggers token refresh and retries original request."""
        # Create mock responses
        # First response: 401 Unauthorized
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Refresh response: 200 OK with new tokens
        mock_refresh_response = Mock()
        mock_refresh_response.status_code = 200
        mock_refresh_response.cookies = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }

        # Retry response: 200 OK with data
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        expected_result = {"data": "success"}
        mock_success_response.json.return_value = expected_result

        # Create mock session with cookies
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
        }.get(key)

        # Configure responses: 401, then refresh success, then original request success
        mock_session.get.side_effect = [mock_401_response, mock_success_response]
        mock_session.post.return_value = mock_refresh_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Make a GET request that will initially fail with 401
        result = client.make_get_request("/api/v1/data")

        # Assert refresh endpoint was called
        mock_session.post.assert_called_with(
            "http://example.com/api/v1/auth/refresh-token"
        )

        # Assert new tokens were set
        mock_session.cookies.set.assert_any_call("access_token", "new_access_token")
        mock_session.cookies.set.assert_any_call("refresh_token", "new_refresh_token")

        # Assert original request was retried and succeeded
        self.assertEqual(result, expected_result)
        self.assertEqual(mock_session.get.call_count, 2)  # Initial call + retry

    @patch("requests.Session")
    def test_token_refresh_failure(self, MockSession):
        """Test that failed token refresh raises appropriate error."""
        # Create mock responses
        # First response: 401 Unauthorized
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Refresh response: 401 Unauthorized (refresh failed)
        mock_refresh_failure_response = Mock()
        mock_refresh_failure_response.status_code = 401

        # Create mock session with cookies
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
        }.get(key)

        # Configure responses: 401 on original, 401 on refresh
        mock_session.get.return_value = mock_401_response
        mock_session.post.return_value = mock_refresh_failure_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Make a GET request that will fail and refresh will fail
        with self.assertRaises(ValueError) as context:
            client.make_get_request("/api/v1/data")

        # Assert correct error message
        self.assertIn("Session expired and refresh failed", str(context.exception))

        # Assert cookies were cleared after failed refresh
        mock_session.cookies.clear.assert_called_once()

    @patch("requests.Session")
    def test_token_refresh_no_refresh_token(self, MockSession):
        """Test that refresh fails gracefully when no refresh token is available."""
        # Create mock responses
        # First response: 401 Unauthorized
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Create mock session without refresh token
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "old_access_token"
        }.get(
            key
        )  # No refresh_token

        # Configure response: 401 on original request
        mock_session.get.return_value = mock_401_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Make a GET request that will fail and refresh will fail (no refresh token)
        with self.assertRaises(ValueError) as context:
            client.make_get_request("/api/v1/data")

        # Assert correct error message
        self.assertIn("Session expired and refresh failed", str(context.exception))

        # Assert refresh endpoint was not called (no refresh token available)
        mock_session.post.assert_not_called()

    @patch("requests.Session")
    def test_refresh_endpoint_no_infinite_loop(self, MockSession):
        """Test that calling the refresh endpoint itself doesn't trigger
        infinite refresh loop."""
        # Create mock response: 401 Unauthorized
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        # Create mock session
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
        }.get(key)

        # Configure response: 401 on refresh endpoint call
        mock_session.post.return_value = mock_401_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Make a POST request directly to refresh endpoint
        with self.assertRaises(
            Exception
        ):  # Should raise due to 401, not ValueError from refresh failure
            client.make_post_request("/api/v1/auth/refresh-token")

        # Assert only one POST call was made (no retry loop)
        self.assertEqual(mock_session.post.call_count, 1)

    @patch("requests.Session")
    def test_no_refresh_on_non_401_errors(self, MockSession):
        """Test that non-401 errors don't trigger token refresh."""
        # Create mock response: 500 Internal Server Error
        mock_500_response = Mock()
        mock_500_response.status_code = 500

        # Create mock session
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        }.get(key)

        # Configure response: 500 error
        mock_session.get.return_value = mock_500_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Make a GET request that returns 500 error
        with self.assertRaises(Exception):  # Should raise due to 500 error
            client.make_get_request("/api/v1/data")

        # Assert refresh endpoint was not called (not a 401 error)
        mock_session.post.assert_not_called()

        # Assert only one GET call was made (no retry)
        self.assertEqual(mock_session.get.call_count, 1)

    @patch("requests.Session")
    def test_thread_safety_single_refresh(self, MockSession):
        """Test that concurrent requests only trigger one refresh operation."""
        # Create mock responses
        mock_401_response = Mock()
        mock_401_response.status_code = 401

        mock_refresh_response = Mock()
        mock_refresh_response.status_code = 200
        mock_refresh_response.cookies = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
        }

        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {"data": "success"}

        # Create mock session
        mock_session = MockSession()
        mock_session.cookies.get.side_effect = lambda key: {
            "access_token": "old_token",
            "refresh_token": "old_refresh",
        }.get(key)

        # Configure responses
        mock_session.get.side_effect = [
            mock_401_response,
            mock_401_response,
            mock_success_response,
            mock_success_response,
        ]
        mock_session.post.return_value = mock_refresh_response

        # Instantiate the APIClient
        client = APIClient("http://example.com", mock_session)

        # Simulate concurrent requests
        results = []
        threads = []

        def make_request():
            try:
                result = client.make_get_request("/api/v1/data")
                results.append(result)
            except Exception as e:
                results.append(str(e))

        # Start two concurrent threads
        for _ in range(2):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for threads to complete
        for thread in threads:
            thread.join()

        # Assert that both requests succeeded
        self.assertEqual(len(results), 2)

        # Assert refresh was called only once (thread safety)
        self.assertEqual(mock_session.post.call_count, 1)
