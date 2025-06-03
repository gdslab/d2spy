import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union
from uuid import UUID

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.third_party.tusclient import client as tusc
from d2spy.extras.utils import ensure_dict
from d2spy.models.data_product import DataProduct
from d2spy.models.data_product_collection import DataProductCollection


class Flight:
    id: UUID
    name: Optional[str]
    acquisition_date: date
    altitude: float
    side_overlap: float
    forward_overlap: float
    sensor: str
    platform: str
    is_active: bool
    deactivated_at: Optional[datetime]
    project_id: UUID
    pilot_id: UUID
    data_products: List[DataProduct]

    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # Flight attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"Flight(acquisition_date={self.acquisition_date!r}, name={self.name!r}, "
            f"altitude={self.altitude!r}, side_overlap={self.side_overlap!r}, "
            f"forward_overlap={self.forward_overlap!r}, sensor={self.sensor!r}, "
            f"platform={self.platform!r})"
        )

    def add_data_product(
        self,
        filepath: str,
        data_type: Union[Literal["dsm", "point_cloud", "ortho"], str],
    ) -> None:
        """Uploads data product to D2S. After the upload finishes, the data product may
        not be available for several minutes while it is processed on the D2S server. It
        will be returned by `Flight.get_data_products` once ready.

        Args:
            filepath (str): Full path to data product on local file system.
            data_type (Union[Literal["dsm", "point_cloud", "ortho"], str]): Data type.
        """
        verify_file_exists(filepath)
        validate_file_extension_and_data_type(filepath, data_type)
        # url for tusd server
        endpoint = f"{self.client.base_url}/files"
        # authorization cookie
        cookies = {"access_token": self.client.session.cookies["access_token"]}
        # project, flight, data type headers
        headers: Dict[str, str] = {
            "X-Project-ID": str(self.project_id),
            "X-Flight-ID": str(self.id),
            "X-Data-Type": data_type,
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": self.client.base_url,
        }
        # metadata about data product file
        metadata = {
            "filename": Path(filepath).name,
            "filetype": get_metadata_filetype(filepath),
            "name": Path(filepath).name,
            "relativePath": "null",
            "type": get_metadata_filetype(filepath),
        }
        # create tus client and set headers and cookies
        tus_client = tusc.TusClient(endpoint)
        tus_client.set_headers(headers)
        tus_client.set_cookies(cookies)
        # create uploader for data product file with metadata
        chunk_size = 10 * 1024 * 1024  # 10 MiB
        tus_uploader = tus_client.uploader(
            filepath, chunk_size=chunk_size, metadata=metadata
        )
        # upload in chunks and print progress
        file_size = tus_uploader.get_file_size()
        while tus_uploader.offset < file_size:
            tus_uploader.upload_chunk()
            progress = (tus_uploader.offset / file_size) * 100
            print(f"Upload progress: {progress:.2f}%", end="\r")

    def add_raw_data(self, filepath: str) -> None:
        """Uploads zipped raw data to D2S. After the upload finishes, the raw data may
        not be available for several minutes while it is processed on the D2S server. It
        will be returned by `Flight.get_raw_data` once ready.

        Args:
            filepath (str): Full path to data product on local file system.
        """
        verify_file_exists(filepath)
        validate_file_extension_for_raw_data(filepath)
        # url for tusd server
        endpoint = f"{self.client.base_url}/files"
        # authorization cookie
        cookies = {"access_token": self.client.session.cookies["access_token"]}
        # project, flight, data type headers
        headers: Dict[str, str] = {
            "X-Project-ID": str(self.project_id),
            "X-Flight-ID": str(self.id),
            "X-Data-Type": "raw",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Origin": self.client.base_url,
        }
        # metadata about raw data file
        metadata = {
            "filename": Path(filepath).name,
            "filetype": "application/zip",
            "name": Path(filepath).name,
            "relativePath": "null",
            "type": "application/zip",
        }
        # create tus client and set headers and cookies
        tus_client = tusc.TusClient(endpoint)
        tus_client.set_headers(headers)
        tus_client.set_cookies(cookies)
        # create uploader for raw file with metadata
        chunk_size = 10 * 1024 * 1024  # 10 MiB
        tus_uploader = tus_client.uploader(
            filepath, chunk_size=chunk_size, metadata=metadata
        )
        # upload in chunks and print progress
        file_size = tus_uploader.get_file_size()
        while tus_uploader.offset < file_size:
            tus_uploader.upload_chunk()
            progress = (tus_uploader.offset / file_size) * 100
            print(f"Upload progress: {progress:.2f}%", end="\r")

    def get_data_product(self, data_product_id: str) -> Optional[DataProduct]:
        """Request single data product by ID. Data product must be active
        and viewable by user.

        Args:
            data_product_id (str): Data product ID.

        Returns:
            Optional[models.DataProduct]: Data product ID or None.
        """
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}"
        endpoint += f"/data_products/{data_product_id}"
        response_data = self.client.make_get_request(endpoint)
        response_data = ensure_dict(response_data)
        data_product = schemas.DataProduct.from_dict(response_data)
        return models.DataProduct(self.client, **data_product.__dict__)

    def get_data_products(self) -> DataProductCollection:
        """Return list of all active data products in a flight.

        Returns:
            DataProductCollection: Collection of data products.
        """
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}/data_products"
        response_data = self.client.make_get_request(endpoint)

        data_products = [
            models.DataProduct(
                self.client,
                **schemas.DataProduct.from_dict(data_product).__dict__,
            )
            for data_product in response_data
        ]
        return DataProductCollection(collection=data_products)

    def get_raw_data(self) -> List[models.RawData]:
        """Return list of all active raw data in a flight.

        Returns:
            List[models.RawData]: List of raw data.
        """
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}/raw_data"
        response_data = self.client.make_get_request(endpoint)

        all_raw_data = [
            models.RawData(
                self.client,
                **schemas.RawData.from_dict(raw_data).__dict__,
            )
            for raw_data in response_data
        ]
        return all_raw_data

    def move_to_project(self, destination_project_id: UUID) -> None:
        """Moves flight from its current project to different project. You must be an
        owner of both the source project and destination project to make the transfer.

        Args:
            destination_project_id (UUID): ID of project the flight will be moved to.
        """
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}"
        endpoint += f"/move_to_project/{destination_project_id}"
        response_data = self.client.make_put_request(endpoint)

        updated_flight = schemas.Flight.from_dict(response_data).__dict__
        for key, value in updated_flight.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: Attribute '{key}' not found in Flight class.")
        return None

    def update(self, **kwargs) -> None:
        """Update flight attributes."""
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}"
        response_data = self.client.make_put_request(
            endpoint, json=json.loads(json.dumps(kwargs, default=str))
        )

        updated_flight = schemas.Flight.from_dict(response_data).__dict__
        for key, value in updated_flight.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: Attribute '{key}' not found in Flight class.")
        return None


def get_metadata_filetype(filepath: str) -> str:
    """Returns file content type based on data product's extension.

    Args:
        filepath (str): Full path to data product.

    Raises:
        ValueError: Raised if data product extension is not recognized.

    Returns:
        str: File content type for data product.
    """
    ext = Path(filepath).suffix

    if ext == ".tif":
        return "image/tiff"
    elif ext == ".las":
        return "application/vnd.las"
    elif ext == ".laz":
        return "application/octet-stream"
    else:
        raise ValueError(f"Unrecognized extension: {ext}")


def validate_file_extension_and_data_type(filepath: str, data_type: str) -> None:
    """Checks if file extension is recognized and raises errors if file extension
    and data type are not compatible. Data type must be less than 16 characters.

    Args:
        filepath (str): Full path to data product.
        data_type (str): Data product's data type (e.g., dsm, ortho, etc.)

    Raises:
        ValueError: Raised if data type is point cloud and file ext. is tif.
        ValueError: Raised if data type is not point cloud and file ext. is las/laz.
        ValueError: Raised if file ext. is not supported.
        ValueError: Raised if data type is greater than 16 characters.
    """
    ext = Path(filepath).suffix

    if ext == ".tif" and data_type == "point_cloud":
        raise ValueError("Point clouds must have .las or .laz extension")

    if (ext == ".las" or ext == ".laz") and data_type != "point_cloud":
        raise ValueError(
            'Data products with .las or .laz extension must be assigned "point_cloud" '
            "data type"
        )

    if ext != ".tif" and ext != ".las" and ext != ".laz":
        raise ValueError("Unrecognized file extension for data product")

    if len(data_type) > 16:
        raise ValueError("Data type must be less than 16 characters")


def validate_file_extension_for_raw_data(filepath: str) -> None:
    """Checks if file extension for raw data is a zip archive.

    Args:
        filepath (str): Full path to raw data.

    Raises:
        ValueError: Raised if file extension is not .zip.
    """
    ext = Path(filepath).suffix

    if ext != ".zip":
        raise ValueError("Raw data must be in zip archive")


def verify_file_exists(filepath: str) -> None:
    """Check if a file exists at the provided filepath.

    Args:
        filepath (str): Full path to data product.

    Raises:
        FileNotFoundError: Raised if file does not exist at filepath.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Cannot find data product at provided path: {filepath}"
        )
