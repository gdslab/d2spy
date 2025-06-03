import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from rasterio.errors import RasterioIOError

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.utils import clip_by_mask
from d2spy.schemas.stac_properties import STACProperties, STACEOProperties
from d2spy.utils.logging_config import get_logger

logger = get_logger(__name__)


class DataProduct:
    id: UUID
    data_type: str
    filepath: str
    original_filename: str
    is_active: bool
    flight_id: UUID
    deactivated_at: Optional[datetime]
    public: bool
    stac_properties: STACProperties
    status: str
    url: str
    # Optional fields for additional metadata
    bbox: Optional[List[float]] = None
    crs: Optional[Dict] = None
    resolution: Optional[Dict] = None

    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # data product attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"DataProduct(data_type={self.data_type!r}, "
            f"filepath={self.filepath!r}, "
            f"original_filename={self.original_filename!r}, "
            f"is_active={self.is_active!r}, public={self.public!r}, "
            f"stac_properties={self.stac_properties!r}, status={self.status!r}, "
            f"url={self.url!r}, bbox={self.bbox!r}, crs={self.crs!r}, "
            f"resolution={self.resolution!r})"
        )

    def clip(
        self, geojson_feature: Dict[Any, Any], out_raster: str, export_vrt: bool = False
    ) -> bool:
        """Clips data product by GeoJSON Polygon Feature.

        Args:
            geojson_feature (Dict[Any, Any]): GeoJSON Polygon Feature.
            out_raster (str): Path for output raster.
            export_vrt (bool): Export VRT file.

        Returns:
            bool: True if successful. False if clip fails.
        """
        if self.data_type == "point_cloud":
            logger.error("Not available for point clouds")
            return False

        try:
            clip_by_mask(self.url, geojson_feature, out_raster, export_vrt)
            return True
        except RasterioIOError as e:
            if str(e) == "HTTP response code: 401":
                if os.environ.get("D2S_API_KEY"):
                    try:
                        url_with_key = (
                            self.url + "?API_KEY=" + os.environ["D2S_API_KEY"]
                        )
                        clip_by_mask(
                            url_with_key,
                            geojson_feature,
                            out_raster,
                            export_vrt,
                        )
                        return True
                    except RasterioIOError as e2:
                        if str(e2) == "HTTP response code: 401":
                            logger.error(
                                "You do not have permission to access this raster"
                            )
                            return False
                        else:
                            raise e2
                else:
                    logger.error(
                        "Set the 'D2S_API_KEY' environment variable before clipping"
                    )
                    return False
            else:
                raise e
        except Exception as e:
            logger.error(f"Failed to clip raster: {e}")
            return False

    def get_band_info(self) -> Optional[List[STACEOProperties]]:
        """Return STAC Electro-Optical bands information.

        Returns:
            Optional[List[STACEOProperties]]: _description_
        """
        if self.data_type == "point_cloud":
            logger.error("Point cloud does not have band info")
            return None

        if not self.stac_properties.get("eo"):
            logger.error("Missing band properties")
            return None

        eo_properties = self.stac_properties["eo"]

        if not isinstance(eo_properties, List):
            logger.error("Band properties in unexpected format")
            return None

        return eo_properties

    def update_band_info(
        self, band_info: List[STACEOProperties]
    ) -> Optional[List[STACEOProperties]]:
        """Update current band description information. Only the "description"
        values may be updated. The "name" values must remain the same. You do
        not need to include all bands in `band_info`, only the ones you wish to
        update.

        Args:
            band_info (List[STACEOProperties]): Band info with new descriptions.

        Returns:
            Optional[List[STACEOProperties]]: Updated band info.
        """
        # Match project ID from data product's URL
        match = re.search(r"/projects/([a-f0-9\-]+)/", self.url)

        # Extract matched project ID
        if match:
            project_id = match.group(1)
        else:
            logger.error("Unable to find project ID associated with data product")
            return None

        # Prepare endpoint for put request
        endpoint = f"/api/v1/projects/{project_id}/flights/{self.flight_id}"
        endpoint += f"/data_products/{self.id}/bands"

        # Construct payload
        data = {"bands": band_info}

        # Put form data
        response_data = self.client.make_put_request(endpoint, json=data)

        # Create the updated_data_product dictionary
        updated_data_product = schemas.DataProduct.from_dict(response_data).__dict__

        # Update the attributes of self
        for key, value in updated_data_product.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(
                    f"Warning: Attribute '{key}' not found in DataProduct class."
                )

        # Create new DataProduct and return updated band info
        return models.DataProduct(self.client, **updated_data_product).get_band_info()

    def derive_ndvi(self, red_band_idx: int, nir_band_idx: int) -> bool:
        """Use data product's bands to derive a new NDVI data product. Must provide
        the red and NIR band indexes.

        Args:
            red_band_idx (int): Red band index.
            nir_band_idx (int): NIR band index.

        Returns:
            bool: True if the job was added to the queue, otherwise False.
        """
        # Check if this is a raster data product
        if self.data_type == "point_cloud":
            logger.error("Not available for point clouds")
            return False

        # Get band properties from STAC EO extension
        eo_properties = self.get_band_info()

        # Check if the data product has at least two bands
        if not isinstance(eo_properties, List) or len(eo_properties) < 2:
            logger.error("Data product must have at least two bands - Red and NIR")
            logger.error(eo_properties)
            return False

        # Reject if the red band index and NIR band index are the same
        if red_band_idx == nir_band_idx:
            logger.error("Red band index and NIR band index cannot be the same")

        # Reject if the red band is outside of the range of possible bands
        if red_band_idx + 1 > len(eo_properties) or red_band_idx < 1:
            logger.error("Red band index outside the range of available bands")

        # Reject if the NIR band is outside of the range of possible bands
        if nir_band_idx + 1 > len(eo_properties) or nir_band_idx < 1:
            logger.error("NIR band index outside the range of available bands")

        # Prepare payload for post request
        data = {
            "chm": False,
            "exg": False,
            "exgRed": 0,
            "exgGreen": 0,
            "exgBlue": 0,
            "ndvi": True,
            "ndviNIR": nir_band_idx,
            "ndviRed": red_band_idx,
            "zonal": False,
            "zonal_layer_id": "",
        }

        # Match project ID from data product's URL
        match = re.search(r"/projects/([a-f0-9\-]+)/", self.url)

        # Extract matched project ID
        if match:
            project_id = match.group(1)
        else:
            logger.error("Unable to find project ID associated with data product")
            return False

        # Prepare endpoint for post request
        endpoint = f"/api/v1/projects/{project_id}/flights/{self.flight_id}"
        endpoint += f"/data_products/{self.id}/tools"

        # post form data
        self.client.make_post_request(endpoint, json=data)

        logger.info("Job request has been added to the queue")

        return True

    def derive_exg(
        self, red_band_idx: int, green_band_idx: int, blue_band_idx: int
    ) -> bool:
        """Use data product's bands to derive a new Excess Green Index data product.
        Must provide the red, green, and blue band indexes.

        Args:
            red_band_idx (int): Red band index.
            green_band_idx (int): Green band index.
            blue_band_idx (int): Blue band index.

        Returns:
            bool: True if the job was added to the queue, otherwise False.
        """
        # Check if this is a raster data product
        if self.data_type == "point_cloud":
            logger.error("Not available for point clouds")
            return False

        # Get band properties from STAC EO extension
        eo_properties = self.get_band_info()

        # Check if the data product has at least two bands
        if not isinstance(eo_properties, List) or len(eo_properties) < 3:
            logger.error(
                "Data product must have at least three bands - Red, Green, and Blue"
            )
            logger.error(eo_properties)
            return False

        # Reject if any of the band indexes are the same
        if len({red_band_idx, green_band_idx, blue_band_idx}) < 3:
            logger.error("Each band index must be unique")

        # Reject if the red band is outside of the range of possible bands
        if red_band_idx + 1 > len(eo_properties) or red_band_idx < 1:
            logger.error("Red band index outside the range of available bands")

        # Reject if the green band is outside of the range of possible bands
        if green_band_idx + 1 > len(eo_properties) or green_band_idx < 1:
            logger.error("Green band index outside the range of available bands")

        # Reject if the blue band is outside of the range of possible bands
        if blue_band_idx + 1 > len(eo_properties) or blue_band_idx < 1:
            logger.error("Blue band index outside the range of available bands")

        # Prepare payload for post request
        data = {
            "chm": False,
            "exg": True,
            "exgRed": red_band_idx,
            "exgGreen": green_band_idx,
            "exgBlue": blue_band_idx,
            "ndvi": False,
            "ndviNIR": 0,
            "ndviRed": 0,
            "zonal": False,
            "zonal_layer_id": "",
        }

        # Match project ID from data product's URL
        match = re.search(r"/projects/([a-f0-9\-]+)/", self.url)

        # Extract matched project ID
        if match:
            project_id = match.group(1)
        else:
            logger.error("Unable to find project ID associated with data product")
            return False

        # Prepare endpoint for post request
        endpoint = f"/api/v1/projects/{project_id}/flights/{self.flight_id}"
        endpoint += f"/data_products/{self.id}/tools"

        # post form data
        self.client.make_post_request(endpoint, json=data)

        logger.info("Job request has been added to the queue")

        return True
