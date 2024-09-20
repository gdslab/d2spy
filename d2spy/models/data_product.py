import os
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from rasterio.errors import RasterioIOError

from d2spy.api_client import APIClient
from d2spy.extras.utils import clip_by_mask
from d2spy.schemas.stac_properties import STACProperties


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
            f"url={self.url!r})"
        )

    def clip(self, geojson_feature: Dict[Any, Any], out_raster: str) -> bool:
        """Clips data product by GeoJSON Polygon Feature.

        Args:
            geojson_feature (Dict[Any, Any]): GeoJSON Polygon Feature.
            out_raster (str): Path for output raster.

        Returns:
            bool: True if successful. False if clip fails.
        """
        if self.data_type == "point_cloud":
            print("Not available for point clouds")
            return False

        try:
            clip_by_mask(self.url, geojson_feature, out_raster)
            print("Raster clipped successfully")
            return True
        except RasterioIOError as e:
            if str(e) == "HTTP response code: 401":
                if os.environ.get("D2S_API_KEY"):
                    try:
                        clip_by_mask(
                            self.url + "?API_KEY=" + os.environ["D2S_API_KEY"],
                            geojson_feature,
                            out_raster,
                        )
                        print("Raster clipped successfully")
                        return True
                    except RasterioIOError as e2:
                        if str(e) == "HTTP response code: 401":
                            print("You do not have permission to access this raster")
                            return False
                        else:
                            raise e2
                else:
                    print("Set the 'D2S_API_KEY' environment variable before clipping")
                    return False
            else:
                raise e
        except Exception as e:
            print(f"Failed to clip raster: {e}")
            return False
