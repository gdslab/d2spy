import json
import os
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from zipfile import is_zipfile, ZipFile

import exifread
import geopandas as gpd
import numpy as np
import rasterio
import rasterio.mask
from geojson_pydantic import Feature, Polygon
from requests import Response
from shapely.geometry import shape


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


def pretty_print_response(response: Response):
    """Pretty prints an API response's status code and message.

    Args:
        response (Response): Response from an API request.
    """
    print(f"{response.status_code}: {http_status_lookup.get(response.status_code)}")
    print(json.dumps(response.json(), indent=4))


def validate_geojson_polygon_feature(
    geojson_data: Dict[Any, Any],
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
        # Try to create the directory
        os.makedirs(os.path.dirname(out_raster), exist_ok=True)

    # If it still doesn't exist, raise an error
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


def get_exif_data(image_path: str) -> Dict:
    """Returns EXIF data extracted from an image.

    Args:
        image_path (str): Path to image.

    Returns:
        Dict: EXIF data.
    """
    with open(image_path, "rb") as image_file:
        tags = exifread.process_file(image_file)
        return tags


def get_gps_coordinates(tags: Dict) -> Optional[Tuple[float, float]]:
    """Reads GPS coordinates in EXIF data and returns latitude, longitude in
    decimal degrees (DD).

    Args:
        tags (Dict): EXIF data.

    Returns:
        Optional[Tuple[float, float]]: Latitude and longitude in DD (if available).
    """
    # Look up GPS related metadata tags
    gps_latitude = tags.get("GPS GPSLatitude")
    gps_latitude_ref = tags.get("GPS GPSLatitudeRef")
    gps_longitude = tags.get("GPS GPSLongitude")
    gps_longitude_ref = tags.get("GPS GPSLongitudeRef")

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = [float(x.num) / float(x.den) for x in gps_latitude.values]
        lon = [float(x.num) / float(x.den) for x in gps_longitude.values]

        # Convert latitude and longitude to decimal degrees
        lat_deg = lat[0] + lat[1] / 60.0 + lat[2] / 3600.0
        lon_deg = lon[0] + lon[1] / 60.0 + lon[2] / 3600.0

        if gps_latitude_ref.values[0] != "N":
            lat_deg = -lat_deg
        if gps_longitude_ref.values[0] != "E":
            lon_deg = -lon_deg

        return lat_deg, lon_deg
    else:
        return None


def extract_lat_lon(image_dir: str) -> List[List[float]]:
    """Returns geographic bounding box based on lat/lon coordinates
    extracted from EXIF data.

    Args:
        image_dir (str): Directory containing images.

    Returns:
        List[List[float]]: Geographic bounding box.
    """
    print("Finding image files...", end="", flush=True)

    images = find_files(image_dir, [".jpg", ".tif"])

    print("Done!")

    if len(images) == 0:
        raise ValueError("No images found in provided directory/zip")

    lats = []
    lons = []

    for index, image in enumerate(images):
        if index % 10 == 0:
            print(
                f"Extracting coordinates from image [{index + 1}/{len(images)}]...",
                end="\r",
                flush=True,
            )

        tags = get_exif_data(image)
        gps_coords = get_gps_coordinates(tags)

        if gps_coords:
            lats.append(gps_coords[0])
            lons.append(gps_coords[1])

    print(f"Extracting coordinates from image [{index + 1}/{len(images)}]...Done!")

    if len(lats) == 0 or len(lons) == 0:
        raise ValueError("Unable to extract coordinates from EXIF data")

    if len(lats) < 3 or len(lons) < 3:
        raise ValueError(
            "Must have at least three coordinate pairs to create bounding box"
        )

    xmin, xmax = min(lons), max(lons)
    ymin, ymax = min(lats), max(lats)

    return [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin]]


def get_bounding_box_from_exif_data(
    image_dir: str, tmpdir: Optional[str] = None
) -> List[List[List[float]]]:
    """Returns geographic bounding box based on lat/lon coordinates
    extracted from EXIF data. The images can be in either a directory or zip file.

    Args:
        image_dir (str): Directory or zip file containing images.
        tmpdir (Optional[str], optional): Optional root temp dir. Defaults to None.

    Raises:
        FileNotFoundError: Raised if unable to find image directory or zip file.
        FileNotFoundError: Raised if 'tmpdir' provided, but directory does not exist.
        ValueError: Raised if 'image_dir' is not a folder or zip file.

    Returns:
        List[List[float]]: Geographic bounding box extracted from image files.
    """
    if image_dir and not os.path.exists(image_dir):
        raise FileNotFoundError(
            "Could not find image directory at path provided by 'image_dir'"
        )

    if tmpdir and not os.path.exists(tmpdir):
        raise FileNotFoundError("Provided alternate temp directory does not exist")

    if os.path.isdir(image_dir):
        bounding_box = extract_lat_lon(image_dir)

    elif is_zipfile(image_dir):
        with tempfile.TemporaryDirectory(dir=tmpdir) as tmp_dir:
            # Unzip all images (.jpg or .tif) to temporary directory
            with ZipFile(image_dir) as zip_file:
                zip_contents = zip_file.namelist()

                for index, zf in enumerate(zip_contents):

                    if index % 10 == 0:
                        print(
                            f"Extracting file [{index + 1}/{len(zip_contents)}]...",
                            end="\r",
                            flush=True,
                        )

                    if zf.lower().endswith(".jpg") or zf.lower().endswith(".tif"):
                        zip_file.extract(zf, tmp_dir)

                print(
                    f"Extracting file [{index + 1}/{len(zip_contents)}]...Done!",
                )

                bounding_box = extract_lat_lon(tmp_dir)
    else:
        raise ValueError(
            "Must provide path to image directory or zip file containing images"
        )

    return [bounding_box]
