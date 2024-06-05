import json
import os
import requests
from datetime import date
from pathlib import Path
from typing import List, Literal, Union
from uuid import UUID

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.third_party.tusclient import client as tusc
from d2spy.extras.third_party.tusclient.uploader import Uploader
from d2spy.extras.utils import pretty_print_response


class Flight:
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # flight attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"Flight(acquisition_date={self.acquisition_date!r}, "
            f"altitude={self.altitude!r}, side_overlap={self.side_overlap!r}, "
            f"forward_overlap={self.forward_overlap!r}, sensor={self.sensor!r}, "
            f"platform={self.platform!r})"
        )

    def add_data_product(
        self,
        filepath: str,
        data_type: Union[Literal["dsm", "point_cloud", "ortho"], str],
    ):
        """Uploads data product to D2S. After the upload finishes, the data product may
        not be available for several minutes while it is processed on the D2S server. It
        will be returned by `Flight.get_data_products` once ready.

        Args:
            filepath (str): Full path to data product on local file system.
            data_type (Union[Literal["dsm", "point_cloud", "ortho"], str]): Data product's data type.
        """
        verify_file_exists(filepath)
        validate_file_extension_and_data_type(filepath, data_type)
        # url for tusd server
        endpoint = f"{self.client.base_url}/files"
        # authorization cookie
        cookies = {"access_token": self.client.session.cookies["access_token"]}
        # project, flight, data type headers
        headers = {
            "X-Project-ID": self.project_id,
            "X-Flight-ID": self.id,
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
        tus_uploader = tus_client.uploader(filepath, metadata=metadata)
        # upload data product file
        r = tus_uploader.upload()

        print(f"{Path(filepath).name} uploaded")

    def get_data_products(self) -> List[models.DataProduct]:
        """Return list of all active data products in a flight.

        Returns:
            List[models.DataProduct]: List of data products.
        """
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}/data_products"
        response = self.client.make_get_request(endpoint)

        if response.status_code == 200:
            response_data: List[dict] = response.json()
            if len(response_data) > 0:
                data_products = [
                    models.DataProduct(
                        self.client,
                        **schemas.DataProduct.from_dict(data_product).__dict__,
                    )
                    for data_product in response_data
                ]
                return data_products

        pretty_print_response(response)
        return []

    def update(self, **kwargs) -> None:
        """Update flight attributes."""
        endpoint = f"/api/v1/projects/{self.project_id}/flights/{self.id}"
        response = self.client.make_put_request(
            endpoint, json=json.loads(json.dumps(kwargs, default=str))
        )

        if response.status_code == 200:
            response_data: Optional[schemas.Flight] = response.json()
            if response_data:
                updated_flight = schemas.Flight.from_dict(response_data).__dict__
                for key, value in updated_flight.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                    else:
                        print(f"Warning: Attribute '{key}' not found in Flight class.")
                return None

        pretty_print_response(response)
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
    and data type are not compatible.

    Args:
        filepath (str): Full path to data product.
        data_type (str): Data product's data type (e.g., dsm, ortho, etc.)

    Raises:
        ValueError: Raised if data type is point cloud and file extension is tif.
        ValueError: Raised if data type is not point cloud and file extension is las/laz.
        ValueError: Raised if file extension is not supported.
    """
    ext = Path(filepath).suffix

    if ext == ".tif" and data_type == "point_cloud":
        raise ValueError("Point clouds must have .las or .laz extension")

    if (ext == ".las" or ext == ".laz") and data_type != "point_cloud":
        raise ValueError(
            'Data products with .las or .laz extension must be assigned "point_cloud" data type'
        )

    if ext != ".tif" and ext != ".las" and ext != ".laz":
        raise ValueError("Unrecognized file extension for data product")


def verify_file_exists(filepath: str) -> None:
    """Check if a file exists at the provided filepath.

    Args:
        filepath (str): Full path to data product.

    Raises:
        FileNotFoundError: Raised if file does not exist at filepath.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError("Cannot find data product at provided path.")
