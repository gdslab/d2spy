import json
import os
import tempfile
from unittest import TestCase

import geopandas as gpd
import rasterio

from d2spy.extras.utils import clip_by_mask


class TestUtils(TestCase):
    def test_clip_by_mask(self):
        in_raster = os.path.join("tests", "data", "dsm.tif")
        geojson_data = json.loads(
            open(os.path.join("tests", "data", "feature_in_dsm.geojson")).read()
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            clip_by_mask(
                in_raster, geojson_data, os.path.join(tmp_dir, "clip_result.zip")
            )

            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "clip_result.zip")))

            with rasterio.open(
                os.path.join(tmp_dir, "clip_result.zip")
            ) as clipped_dataset:
                feature = gpd.read_file(
                    os.path.join("tests", "data", "feature_in_dsm.geojson")
                )
                feature = feature.to_crs(clipped_dataset.crs)
                geometry = feature.geometry[0]
                self.assertEqual(
                    [int(bound) for bound in geometry.bounds],
                    [int(bound) for bound in clipped_dataset.bounds],
                )

    def test_clip_by_mask_with_out_of_bounds_mask(self):
        in_raster = os.path.join("tests", "data", "dsm.tif")
        geojson_data = json.loads(
            open(os.path.join("tests", "data", "feature_outside_dsm.geojson")).read()
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError) as context:
                clip_by_mask(
                    in_raster, geojson_data, os.path.join(tmp_dir, "clip_result.zip")
                )

        self.assertEqual(str(context.exception), "Input shapes do not overlap raster.")
