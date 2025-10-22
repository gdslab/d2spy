"""
Geospatial utilities for d2spy.

These functions require optional geo dependencies.
Install with: pip install d2spy[geo]
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple
from zipfile import is_zipfile, ZipFile

from d2spy.utils.logging_config import get_logger

# Optional geo dependencies
try:
    import exifread
    import geopandas as gpd
    import numpy as np
    import rasterio
    import rasterio.mask
    from shapely.geometry import shape

    HAS_GEO = True
except ImportError:
    HAS_GEO = False

logger = get_logger(__name__)


def require_geo():
    """Raise helpful error if geo dependencies are missing."""
    if not HAS_GEO:
        raise ImportError(
            "Geospatial utilities require additional dependencies.\n"
            "Install with: pip install d2spy[geo]"
        )


def is_gdal_available():
    """Check if GDAL CLI tools are available (doesn't require geo extras)."""
    import shutil

    return shutil.which("gdalbuildvrt") is not None


def validate_geojson_polygon_feature(geojson_data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Returns GeoJSON Polygon Feature dict (no validation, trust backend).

    Args:
        geojson_data: Dict representing a GeoJSON Polygon feature.

    Returns:
        Dict[Any, Any]: GeoJSON Polygon Feature dict (passthrough).
    """
    # Just return the dict - trust it's valid from the backend
    return geojson_data


def clip_by_mask(
    in_raster: str, geojson: Dict[Any, Any], out_raster: str, export_vrt: bool = False
) -> None:
    """Clip a raster by a GeoJSON polygon mask.

    Args:
        in_raster: Path to input raster file.
        geojson: GeoJSON polygon feature dict.
        out_raster: Path to output clipped raster.
        export_vrt: Whether to export VRT file.

    Raises:
        ImportError: If geo dependencies not installed.
    """
    require_geo()

    feature = validate_geojson_polygon_feature(geojson)

    if not os.path.exists(os.path.dirname(out_raster)):
        os.makedirs(os.path.dirname(out_raster), exist_ok=True)

    if not os.path.exists(os.path.dirname(out_raster)):
        raise FileNotFoundError("directory for output raster does not exist")

    with rasterio.open(in_raster) as dataset:
        # Create geopandas dataframe for boundary and project to dataset crs
        gdf = gpd.GeoDataFrame(
            [feature.get("properties", {})],
            geometry=[shape(feature["geometry"])],
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
            logger.info("Raster clipped successfully")

        # Export VRT file
        if export_vrt:
            if is_gdal_available():
                cmd = ["gdalbuildvrt", out_raster.replace(".tif", ".vrt")] + [in_raster]
                try:
                    subprocess.run(cmd, check=True)
                    logger.info("VRT file exported successfully")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Error exporting VRT file: {e}")
            else:
                logger.warning("GDAL is not available. Unable to export VRT file.")


def get_exif_data(image_path: str) -> Dict:
    """Returns EXIF data extracted from an image.

    Args:
        image_path: Path to image.

    Returns:
        Dict: EXIF data.

    Raises:
        ImportError: If exifread not installed.
    """
    require_geo()

    with open(image_path, "rb") as image_file:
        tags = exifread.process_file(image_file)
        return tags


def get_gps_coordinates(tags: Dict) -> Optional[Tuple[float, float]]:
    """Reads GPS coordinates in EXIF data and returns latitude, longitude in DD.

    Args:
        tags: EXIF data.

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
    """Returns geographic bounding box based on lat/lon coordinates from EXIF.

    Args:
        image_dir: Directory containing images.

    Returns:
        List[List[float]]: Geographic bounding box.

    Raises:
        ImportError: If exifread not installed.
    """
    require_geo()

    from d2spy.extras.utils import find_files

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
    """Returns geographic bounding box from EXIF data in images.

    Args:
        image_dir: Directory or zip file containing images.
        tmpdir: Optional root temp dir. Defaults to None.

    Raises:
        ImportError: If exifread not installed.
        FileNotFoundError: If unable to find image directory or zip file.
        ValueError: If 'image_dir' is not a folder or zip file.

    Returns:
        List[List[float]]: Geographic bounding box extracted from image files.
    """
    require_geo()

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
