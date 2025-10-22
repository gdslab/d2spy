"""
Core utility functions for d2spy.

These functions have no dependencies beyond requests.
For geospatial utilities, see d2spy.extras.geo (requires d2spy[geo]).
"""

import json
import os
import shutil
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Union

from requests import Response

http_status_lookup = {status.value: status.name for status in list(HTTPStatus)}


def ensure_dict(
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]],
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
    response_data: Union[Dict[Any, Any], List[Dict[Any, Any]]],
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


def is_gdal_available():
    """Check if GDAL CLI tools are available."""
    return shutil.which("gdalbuildvrt") is not None


def pretty_print_response(response: Response):
    """Pretty prints an API response's status code and message.

    Args:
        response (Response): Response from an API request.
    """
    print(f"{response.status_code}: {http_status_lookup.get(response.status_code)}")
    try:
        print(json.dumps(response.json(), indent=4))
    except (json.JSONDecodeError, ValueError):
        # Response doesn't contain valid JSON
        print(response.text if response.text else "(no response body)")


def find_files(folder: str, types: List[str]) -> List[str]:
    """Walks down a folder and its subfolders finding files that match the
    extensions provided in 'types'. It will stop after reaching a depth of 7 subfolders.

    Args:
        folder (str): Folder with files.
        types (List[str]): Types of files to match.

    Returns:
        List[str]: List of matched files.
    """
    images = []
    max_depth = 7
    # get current depth level relative to root
    root_depth = folder.rstrip(os.path.sep).count(os.path.sep)

    for path, _, files in os.walk(folder):
        # get depth of current path relative to root depth
        current_depth = path.count(os.path.sep) - root_depth

        if current_depth < max_depth:
            for file in files:
                if Path(file).suffix.lower() in types:
                    images.append(os.path.join(path, file))
        else:
            # remove remaining folders to stop os.walk
            del _[:]

    return images


# Re-export geo utilities for backwards compatibility
# These will raise ImportError if geo extras not installed
def clip_by_mask(*args, **kwargs):
    """Clip a raster by mask. Requires: pip install d2spy[geo]"""
    from d2spy.extras.geo import clip_by_mask as _clip

    return _clip(*args, **kwargs)


def get_exif_data(*args, **kwargs):
    """Get EXIF data from image. Requires: pip install d2spy[geo]"""
    from d2spy.extras.geo import get_exif_data as _get_exif

    return _get_exif(*args, **kwargs)


def get_bounding_box_from_exif_data(*args, **kwargs):
    """Get bounding box from EXIF data. Requires: pip install d2spy[geo]"""
    from d2spy.extras.geo import get_bounding_box_from_exif_data as _get_bbox

    return _get_bbox(*args, **kwargs)


def validate_geojson_polygon_feature(*args, **kwargs):
    """Validate GeoJSON polygon feature (no-op, returns dict)."""
    from d2spy.extras.geo import validate_geojson_polygon_feature as _validate

    return _validate(*args, **kwargs)
