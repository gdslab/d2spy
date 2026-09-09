from unittest import TestCase
from unittest.mock import patch

import requests

from d2spy.schemas.session import DEFAULT_TIMEOUT, D2SpySession


class TestD2SpySession(TestCase):
    @patch("requests.adapters.HTTPAdapter.send")
    def test_default_timeout_applied_to_request(self, mock_send):
        # Mock the transport so no real connection is attempted
        mock_send.return_value = requests.Response()

        # Requests made through the session receive the default timeout
        session = D2SpySession()
        session.get("https://valid-d2s-url.org/api/v1/health")

        # Assert that the adapter was handed the session default timeout
        self.assertEqual(mock_send.call_args.kwargs["timeout"], DEFAULT_TIMEOUT)

    @patch("requests.adapters.HTTPAdapter.send")
    def test_custom_timeout_applied_to_request(self, mock_send):
        mock_send.return_value = requests.Response()

        # A session may override the default timeout for all of its requests
        session = D2SpySession(timeout=(1, 2))
        session.get("https://valid-d2s-url.org/api/v1/health")

        self.assertEqual(mock_send.call_args.kwargs["timeout"], (1, 2))

    @patch("requests.adapters.HTTPAdapter.send")
    def test_explicit_per_request_timeout_wins(self, mock_send):
        mock_send.return_value = requests.Response()

        # An explicit timeout on a single call overrides the session default
        session = D2SpySession()
        session.get("https://valid-d2s-url.org/api/v1/health", timeout=5)

        self.assertEqual(mock_send.call_args.kwargs["timeout"], 5)

    @patch("requests.adapters.HTTPAdapter.send")
    def test_explicit_none_timeout_is_preserved(self, mock_send):
        mock_send.return_value = requests.Response()

        # Passing None explicitly still means "block indefinitely"
        session = D2SpySession()
        session.get("https://valid-d2s-url.org/api/v1/health", timeout=None)

        self.assertIsNone(mock_send.call_args.kwargs["timeout"])

    def test_session_is_a_requests_session(self):
        # The session must remain a drop-in requests.Session for callers
        session = D2SpySession()
        self.assertIsInstance(session, requests.Session)
        self.assertEqual(session.timeout, DEFAULT_TIMEOUT)
