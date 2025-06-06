from typing import Optional
import base64
from functools import wraps

import requests

from d2spy.extras.third_party.tusclient.exceptions import (
    TusUploadFailed,
    TusCommunicationError,
)


# Catches requests exceptions and throws custom tuspy errors.
def catch_requests_error(func):
    """Deocrator to catch requests exceptions"""

    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as error:
            raise TusCommunicationError(error)

    return _wrapper


class BaseTusRequest:
    """
    Http Request Abstraction.

    Sets up tus custom http request on instantiation.

    requires argument 'uploader' an instance of tusclient.uploader.Uploader
    on instantiation.

    :Attributes:
        - response_headers (dict)
        - file (file):
            The file that is being uploaded.
    """

    def __init__(self, uploader):
        self._url = uploader.url
        self.response_headers = {}
        self.status_code = None
        self.response_content = None
        self.verify_tls_cert = bool(uploader.verify_tls_cert)
        self.file = uploader.get_file_stream()
        self.file.seek(uploader.offset)

        self._request_headers = {
            "upload-offset": str(uploader.offset),
            "Content-Type": "application/offset+octet-stream",
        }
        self._request_cookies = {}
        self._request_headers.update(uploader.get_headers())
        self._request_cookies.update(uploader.get_cookies())
        self._content_length = uploader.get_request_length()
        self._upload_checksum = uploader.upload_checksum
        self._checksum_algorithm = uploader.checksum_algorithm
        self._checksum_algorithm_name = uploader.checksum_algorithm_name

    def add_checksum(self, chunk: bytes):
        if self._upload_checksum:
            self._request_headers["upload-checksum"] = " ".join(
                (
                    self._checksum_algorithm_name,
                    base64.b64encode(self._checksum_algorithm(chunk).digest()).decode(
                        "ascii"
                    ),
                )
            )


class TusRequest(BaseTusRequest):
    """Class to handle async Tus upload requests"""

    def perform(self):
        """
        Perform actual request.
        """
        try:
            chunk = self.file.read(self._content_length)
            self.add_checksum(chunk)
            resp = requests.patch(
                self._url,
                data=chunk,
                headers=self._request_headers,
                cookies=self._request_cookies,
                verify=self.verify_tls_cert,
            )
            self.status_code = resp.status_code
            self.response_content = resp.content
            self.response_headers = {k.lower(): v for k, v in resp.headers.items()}
        except requests.exceptions.RequestException as error:
            raise TusUploadFailed(error)
