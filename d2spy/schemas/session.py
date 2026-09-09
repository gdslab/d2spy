from typing import Any, Dict, Optional, Tuple, Union

import requests

# A single value applied to both phases, or a (connect, read) pair.
TimeoutType = Union[float, Tuple[float, float]]

# Default (connect, read) timeout in seconds for D2S API requests.
DEFAULT_TIMEOUT: TimeoutType = (10, 60)


class D2SpySession(requests.Session):
    d2s_data: Dict[str, Any]

    def __init__(self, timeout: Optional[TimeoutType] = DEFAULT_TIMEOUT) -> None:
        """Constructor for D2SpySession class.

        Args:
            timeout (Optional[TimeoutType]): Default (connect, read) timeout in
                seconds applied to every request made through this session.
                Pass None to block indefinitely.
        """
        super().__init__()
        self.timeout: Optional[TimeoutType] = timeout

    # Signature widened to a passthrough so it survives new requests parameters.
    def request(  # type: ignore[override]
        self, method: str, url: str, *args: Any, **kwargs: Any
    ) -> requests.Response:
        """Send a request, applying the session default timeout when the caller
        did not provide one. An explicit timeout of None is preserved.

        Args:
            method (str): HTTP method for the request.
            url (str): URL for the request.

        Returns:
            requests.Response: The response object.
        """
        kwargs.setdefault("timeout", self.timeout)
        return super().request(method, url, *args, **kwargs)
