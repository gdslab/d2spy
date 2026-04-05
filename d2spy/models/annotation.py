import mimetypes
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from d2spy import schemas
from d2spy.api_client import APIClient
from d2spy.extras.third_party.tusclient import client as tusc
from d2spy.utils.logging_config import get_logger


logger = get_logger(__name__)

# Supported attachment file extensions (matching backend validation)
SUPPORTED_ATTACHMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".webm",
    ".avi",
}


class Annotation:
    id: UUID
    description: str
    geom: Dict[str, Any]
    data_product_id: UUID
    created_by_id: Optional[UUID]
    visibility: str
    created_at: str
    updated_at: str
    attachments: List[Dict[str, Any]]
    tags: List[str]
    style: Optional[Dict[str, Any]] = None
    # Private context for TUS uploads (not from API response)
    _project_id: Optional[str] = None
    _flight_id: Optional[str] = None

    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"Annotation(id={self.id!r}, "
            f"description={self.description!r}, "
            f"visibility={self.visibility!r}, "
            f"tags={self.tags!r})"
        )

    @property
    def _base_endpoint(self) -> str:
        """Base API endpoint for this annotation."""
        return (
            f"/api/v1/projects/{self._project_id}"
            f"/flights/{self._flight_id}"
            f"/data_products/{self.data_product_id}"
            f"/annotations/{self.id}"
        )

    def update(self, **kwargs) -> None:
        """Update annotation attributes.

        Args:
            **kwargs: Fields to update. Supported fields: description, geom,
                tags, visibility, style.
        """
        endpoint = self._base_endpoint
        response_data = self.client.make_put_request(endpoint, json=kwargs)

        updated_annotation = schemas.Annotation.from_dict(response_data).__dict__
        for key, value in updated_annotation.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete(self) -> bool:
        """Delete this annotation.

        Returns:
            bool: True if deletion was successful.
        """
        endpoint = self._base_endpoint
        self.client.make_delete_request(endpoint)
        return True

    def add_attachment(
        self,
        filepath: str,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> None:
        """Upload an attachment file to this annotation via TUS.

        Supported file types: JPG, JPEG, PNG, GIF, WebP, MP4, MOV, WebM, AVI.

        Args:
            filepath (str): Full path to attachment file on local file system.
            progress_callback (Optional[Callable[[float], None]]): Optional
                callback function to report upload progress. The function
                should accept a single float argument representing the upload
                progress percentage (0.0 to 100.0).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not supported.
            ValueError: If project/flight context is missing.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Cannot find attachment file at provided path: {filepath}"
            )

        ext = Path(filepath).suffix.lower()
        if ext not in SUPPORTED_ATTACHMENT_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension: {ext}. "
                f"Supported: {', '.join(sorted(SUPPORTED_ATTACHMENT_EXTENSIONS))}"
            )

        if not self._project_id or not self._flight_id:
            raise ValueError(
                "Missing project/flight context for attachment upload. "
                "Annotation must be created via DataProduct methods."
            )

        # Ensure we have a fresh access token
        self.client.make_get_request("/api/v1/users/current")

        # TUS endpoint
        endpoint = f"{self.client.base_url}/files"

        # Authorization cookie
        cookies = {"access_token": self.client.session.cookies["access_token"]}

        # Headers required for annotation attachment upload
        headers: Dict[str, str] = {
            "X-Project-ID": str(self._project_id),
            "X-Flight-ID": str(self._flight_id),
            "X-Data-Type": "annotation_attachment",
            "X-Annotation-ID": str(self.id),
            "X-Data-Product-ID": str(self.data_product_id),
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": self.client.base_url,
        }

        # Determine content type
        content_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"

        # Metadata about attachment file
        metadata = {
            "filename": Path(filepath).name,
            "filetype": content_type,
            "name": Path(filepath).name,
            "relativePath": "null",
            "type": content_type,
        }

        # Create TUS client and upload
        tus_client = tusc.TusClient(endpoint)
        tus_client.set_headers(headers)
        tus_client.set_cookies(cookies)

        chunk_size = 10 * 1024 * 1024  # 10 MiB
        tus_uploader = tus_client.uploader(
            filepath, chunk_size=chunk_size, metadata=metadata
        )

        file_size = tus_uploader.get_file_size()
        while tus_uploader.offset < file_size:
            tus_uploader.upload_chunk()
            progress = (tus_uploader.offset / file_size) * 100
            if progress_callback:
                progress_callback(progress)
            else:
                print(f"Upload progress: {progress:.2f}%", end="\r")

    def download_attachment(self, attachment_id: str, out_path: str) -> None:
        """Download an attachment file to the local file system.

        Args:
            attachment_id (str): ID of the attachment to download.
            out_path (str): Local file path to save the downloaded file.
        """
        endpoint = f"{self._base_endpoint}/attachments/{attachment_id}/download"
        url = self.client.base_url + endpoint
        response = self.client.session.get(url, stream=True, timeout=60)

        if response.status_code == 401:
            # Try refreshing token and retry
            if self.client._refresh_access_token():
                response = self.client.session.get(url, stream=True, timeout=60)

        if response.status_code != 200:
            response.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def delete_attachment(self, attachment_id: str) -> bool:
        """Delete an attachment from this annotation.

        Args:
            attachment_id (str): ID of the attachment to delete.

        Returns:
            bool: True if deletion was successful.
        """
        endpoint = f"{self._base_endpoint}/attachments/{attachment_id}"
        self.client.make_delete_request(endpoint)
        return True
