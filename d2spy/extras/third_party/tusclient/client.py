from typing import Dict, Optional

from d2spy.extras.third_party.tusclient.uploader import Uploader


class TusClient:
    """
    Object representation of Tus client.

    :Attributes:
        - url (str):
            represents the tus server's create extension url. On instantiation this argument
            must be passed to the constructor.
        - headers (dict):
            This can be used to set the server specific headers. These headers would be sent
            along with every request made by the client to the server. This may be used to set
            authentication headers. These headers should not include headers required by tus
            protocol. If not set this defaults to an empty dictionary.
        - cookies (dict):
            This can be used to set the server specific cookies. These cookies would be sent
            along with every request made by the client to the server. This may be used to set
            authorization cookies.

    :Constructor Args:
        - url (str)
        - headers (Optional[dict])
        - cookies (Optional[dict])
    """

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ):
        self.url = url
        self.headers = headers or {}
        self.cookies = cookies or {}

    def set_headers(self, headers: Dict[str, str]):
        """
        Set tus client headers.

        Update and/or set new headers that would be sent along with every request made
        to the server.

        :Args:
            - headers (dict):
                key, value pairs of the headers to be set. This argument is required.
        """
        self.headers.update(headers)

    def set_cookies(self, cookies: Dict[str, str]):
        """
        Set tus client cookies.

        Update and/or set new cookies that would be sent along with every request made
        to the server.

        :Args:
            - cookies (dict):
                key, value pairs of the cookies to be set. This argument is required.
        """
        self.cookies.update(cookies)

    def uploader(self, *args, **kwargs) -> Uploader:
        """
        Return uploader instance pointing at current client instance.

        Return uploader instance with which you can control the upload of a specific
        file. The current instance of the tus client is passed to the uploader on creation.

        :Args:
            see tusclient.uploader.Uploader for required and optional arguments.
        """
        kwargs["client"] = self
        return Uploader(*args, **kwargs)
