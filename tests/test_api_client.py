from unittest import TestCase
from unittest.mock import patch, Mock

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
