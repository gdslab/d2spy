import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import geopandas as gpd
import rasterio

from d2spy.extras.utils import clip_by_mask

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestUtils(TestCase):
    def test_clip_by_mask(self):
        in_raster = os.path.join(DATA_DIR, "dsm.tif")
        with open(os.path.join(DATA_DIR, "feature_in_dsm.geojson")) as f:
            geojson_data = json.load(f)

        with tempfile.TemporaryDirectory() as tmp_dir:
            clip_by_mask(
                in_raster, geojson_data, os.path.join(tmp_dir, "clip_result.zip")
            )

            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "clip_result.zip")))

            with rasterio.open(
                os.path.join(tmp_dir, "clip_result.zip")
            ) as clipped_dataset:
                feature = gpd.read_file(
                    os.path.join(DATA_DIR, "feature_in_dsm.geojson")
                )
                feature = feature.to_crs(clipped_dataset.crs)
                geometry = feature.geometry[0]
                for geom_bound, clip_bound in zip(
                    geometry.bounds, clipped_dataset.bounds
                ):
                    self.assertAlmostEqual(geom_bound, clip_bound, places=0)

    def test_clip_by_mask_with_out_of_bounds_mask(self):
        in_raster = os.path.join(DATA_DIR, "dsm.tif")
        with open(os.path.join(DATA_DIR, "feature_outside_dsm.geojson")) as f:
            geojson_data = json.load(f)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError) as context:
                clip_by_mask(
                    in_raster, geojson_data, os.path.join(tmp_dir, "clip_result.zip")
                )

        self.assertEqual(str(context.exception), "Input shapes do not overlap raster.")

    @patch("d2spy.extras.geo.HAS_GEO", False)
    def test_require_geo_missing_dependencies(self):
        from d2spy.extras.geo import require_geo

        with self.assertRaises(ImportError) as context:
            require_geo()

        self.assertIn("pip install d2spy[geo]", str(context.exception))
