import json
import os
from http import HTTPStatus
from typing import Any, Dict, List, Union

import geopandas as gpd
import numpy as np
import rasterio
import rasterio.mask
from geojson_pydantic import Feature, Polygon
from requests import Response
from shapely.geometry import shape


http_status_lookup = {status.value: status.name for status in list(HTTPStatus)}


def ensure_dict(
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]]
) -> Dict[Any, Any]:
    """Verifies that the API response data is a dictionary before returning it.

    Args:
        response_data (Union[Dict[Any, Any], List[Dict[Any, Any]]]): API response data.

    Raises:
        Exception: Raised if the response data is not a dictionary.

    Returns:
        Dict[Any, Any]: Response data after verification.
    """
    if not isinstance(response_data, Dict):
        raise Exception("Response data must be type Dict[Any, Any]")
    return response_data


def ensure_list_of_dict(
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]]
) -> List[Dict[Any, Any]]:
    """Verifies that the API response data is a list of dictionaries or
    empty list before returning it.

    Args:
        response_data (Union[Dict[Any, Any], List[Dict[Any, Any]]]): API response data.

    Raises:
        Exception: Raised if the response data is not a list of dicts or an empty list.

    Returns:
        Dict[Any, Any]: Response data after verification.
    """
    if (
        not isinstance(response_data, List)
        or len(response_data) > 0
        and not isinstance(response_data[0], Dict)
    ):
        raise Exception("Response data must be type List[Dict[Any, Any]]")
    return response_data


def pretty_print_response(response: Response):
    """Pretty prints an API response's status code and message.

    Args:
        response (Response): Response from an API request.
    """
    print(f"{response.status_code}: {http_status_lookup.get(response.status_code)}")
    print(json.dumps(response.json(), indent=4))


def validate_geojson_polygon_feature(
    geojson_data: Dict[Any, Any]
) -> Feature[Polygon, Dict[Any, Any]]:
    """Returns GeoJSON Polygon Feature or raises exception if unable to validate.

    Args:
        geojson_data (Dict[Any, Any]): Dict representing a GeoJSON Polygon feature.

    Raises:
        ValueError: Raised for missing key in GeoJSON data.
        ValueError: Raised for general error while validating GeoJSON data.

    Returns:
        Feature[Polygon, Dict[Any, Any]]: Validated GeoJSON Polygon Feature.
    """
    try:
        polygon_feature: Feature[Polygon, Dict[Any, Any]] = Feature(
            type=geojson_data["type"],
            geometry=Polygon(**geojson_data["geometry"]),
            properties=geojson_data.get("properties", {}),
        )
        return polygon_feature
    except KeyError as e:
        raise ValueError(f"GeoJSON Feature missing required field {e}")
    except Exception as e:
        raise ValueError(f"Invalid GeoJSON Feature - {e}")


def clip_by_mask(in_raster: str, geojson: Dict[Any, Any], out_raster: str) -> None:
    feature = validate_geojson_polygon_feature(geojson)
    assert feature.geometry

    if not os.path.exists(os.path.dirname(out_raster)):
        raise FileNotFoundError("directory for output raster does not exist")

    with rasterio.open(in_raster) as dataset:
        # Create geopandas dataframe for boundary and project to dataset crs
        gdf = gpd.GeoDataFrame(
            [feature.properties],
            geometry=[shape(feature.geometry.model_dump())],
            crs="EPSG:4326",
        )
        gdf = gdf.to_crs(dataset.crs)
        geometry = gdf.geometry[0]

        # Create masked array using polygon feature and crop to extent of geometry
        mask_raster, mask_transform = rasterio.mask.mask(dataset, [geometry], crop=True)
        meta = dataset.meta.copy()

        if not isinstance(mask_raster, np.ndarray) and not isinstance(
            mask_raster, np.ma.MaskedArray
        ):
            raise TypeError(
                "out_raster should be numpy.ndarray or numpy.ma.MaskedArray"
            )

        # Update original metadata with height, width, and transform of masked array
        meta.update(
            {
                "driver": "GTiff",
                "height": mask_raster.shape[1],
                "width": mask_raster.shape[2],
                "transform": mask_transform,
            }
        )

        # Write clipped raster to disk
        with rasterio.open(out_raster, "w", **meta) as clipped_dataset:
            clipped_dataset.write(mask_raster)
