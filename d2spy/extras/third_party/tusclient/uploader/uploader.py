from typing import Optional
import time
import asyncio
from urllib.parse import urljoin

import requests

from d2spy.extras.third_party.tusclient.uploader.baseuploader import BaseUploader

from d2spy.extras.third_party.tusclient.exceptions import TusUploadFailed, TusCommunicationError
from d2spy.extras.third_party.tusclient.request import TusRequest, catch_requests_error


def _verify_upload(request: TusRequest):
    if 200 <= request.status_code < 300:
        return True
    else:
        raise TusUploadFailed("", request.status_code, request.response_content)


class Uploader(BaseUploader):
    def upload(self, stop_at: Optional[int] = None):
        """
        Perform file upload.

        Performs continous upload of chunks of the file. The size uploaded at each cycle is
        the value of the attribute 'chunk_size'.

        :Args:
            - stop_at (Optional[int]):
                Determines at what offset value the upload should stop. If not specified this
                defaults to the file size.
        """
        self.stop_at = stop_at or self.get_file_size()

        if not self.url:
            # Ensure the POST request is performed even for empty files.
            # This ensures even empty files can be uploaded; in this case
            # only the POST request needs to be performed.
            self.set_url(self.create_url())
            self.offset = 0

        while self.offset < self.stop_at:
            self.upload_chunk()

    def upload_chunk(self):
        """
        Upload chunk of file.
        """
        self._retried = 0

        # Ensure that we have a URL, as this is behavior we allowed previously.
        # See https://github.com/tus/tus-py-client/issues/82.
        if not self.url:
            self.set_url(self.create_url())
            self.offset = 0

        self._do_request()
        self.offset = int(self.request.response_headers.get("upload-offset"))

    @catch_requests_error
    def create_url(self):
        """
        Return upload url.

        Makes request to tus server to create a new upload url for the required file upload.
        """
        resp = requests.post(
            self.client.url,
            headers=self.get_url_creation_headers(),
            cookies=self.get_url_creation_cookies(),
            verify=self.verify_tls_cert,
        )
        url = resp.headers.get("location")
        if url is None:
            msg = "Attempt to retrieve create file url with status {}".format(
                resp.status_code
            )
            raise TusCommunicationError(msg, resp.status_code, resp.content)
        return urljoin(self.client.url, url)

    def _do_request(self):
        self.request = TusRequest(self)
        try:
            self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            self._retry_or_cry(error)

    def _retry_or_cry(self, error):
        if self.retries > self._retried:
            time.sleep(self.retry_delay)

            self._retried += 1
            try:
                self.offset = self.get_offset()
            except TusCommunicationError as err:
                self._retry_or_cry(err)
            else:
                self._do_request()
        else:
            raise error
