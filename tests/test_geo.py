import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from d2spy.extras import geo, utils

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def fake_gdal(writes_file=True, returns=None, raises=None):
    """Stand-in for the osgeo.gdal module with a scripted BuildVRT."""
    module = MagicMock()

    def build_vrt(vrt_path, sources):
        if raises:
            raise raises
        if writes_file:
            open(vrt_path, "w").close()
        return returns

    module.BuildVRT.side_effect = build_vrt
    return module


class TestGeo(TestCase):
    def test_no_subprocess_dependency(self):
        # VRT export must not shell out; plugins.qgis.org flags subprocess use
        self.assertFalse(hasattr(geo, "subprocess"))

    def test_is_gdal_available(self):
        with patch("d2spy.extras.geo.gdal", MagicMock()):
            self.assertTrue(geo.is_gdal_available())
        with patch("d2spy.extras.geo.gdal", None):
            self.assertFalse(geo.is_gdal_available())

    def test_utils_is_gdal_available_delegates_to_geo(self):
        with patch("d2spy.extras.geo.gdal", None):
            self.assertFalse(utils.is_gdal_available())
        with patch("d2spy.extras.geo.gdal", MagicMock()):
            self.assertTrue(utils.is_gdal_available())

    def test_build_vrt_success(self):
        module = fake_gdal(returns=MagicMock())
        with tempfile.TemporaryDirectory() as tmp_dir:
            vrt = os.path.join(tmp_dir, "out.vrt")
            with patch("d2spy.extras.geo.gdal", module):
                self.assertTrue(geo.build_vrt("in.tif", vrt))
            module.BuildVRT.assert_called_once_with(vrt, ["in.tif"])
            self.assertTrue(os.path.exists(vrt))

    def test_build_vrt_without_gdal(self):
        with patch("d2spy.extras.geo.gdal", None):
            with self.assertLogs(geo.logger, level="WARNING") as log:
                self.assertFalse(geo.build_vrt("in.tif", "out.vrt"))
        self.assertIn("GDAL Python bindings not available", log.output[0])

    def test_build_vrt_returns_none(self):
        # GDAL returns None on failure when exceptions are off
        module = fake_gdal(writes_file=False, returns=None)
        with patch("d2spy.extras.geo.gdal", module):
            with self.assertLogs(geo.logger, level="WARNING") as log:
                self.assertFalse(geo.build_vrt("in.tif", "out.vrt"))
        self.assertIn("returned None", log.output[0])

    def test_build_vrt_raises(self):
        # GDAL raises RuntimeError on failure when exceptions are on
        module = fake_gdal(raises=RuntimeError("boom"))
        with patch("d2spy.extras.geo.gdal", module):
            with self.assertLogs(geo.logger, level="WARNING") as log:
                self.assertFalse(geo.build_vrt("in.tif", "out.vrt"))
        self.assertIn("boom", log.output[0])

    def test_build_vrt_writes_nothing(self):
        # GDAL can skip an unreadable source with only a warning
        module = fake_gdal(writes_file=False, returns=MagicMock())
        with tempfile.TemporaryDirectory() as tmp_dir:
            vrt = os.path.join(tmp_dir, "out.vrt")
            with patch("d2spy.extras.geo.gdal", module):
                with self.assertLogs(geo.logger, level="WARNING") as log:
                    self.assertFalse(geo.build_vrt("in.tif", vrt))
        self.assertIn("no VRT was written", log.output[0])

    def test_clip_by_mask_export_vrt(self):
        in_raster = os.path.join(DATA_DIR, "dsm.tif")
        with open(os.path.join(DATA_DIR, "feature_in_dsm.geojson")) as f:
            geojson_data = json.load(f)

        module = fake_gdal(returns=MagicMock())
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_raster = os.path.join(tmp_dir, "clip_result.tif")
            with patch("d2spy.extras.geo.gdal", module):
                geo.clip_by_mask(in_raster, geojson_data, out_raster, export_vrt=True)

            # The VRT references the original input raster, next to the clip
            module.BuildVRT.assert_called_once_with(
                os.path.join(tmp_dir, "clip_result.vrt"), [in_raster]
            )
            self.assertTrue(os.path.exists(out_raster))

    def test_clip_by_mask_skips_vrt_by_default(self):
        in_raster = os.path.join(DATA_DIR, "dsm.tif")
        with open(os.path.join(DATA_DIR, "feature_in_dsm.geojson")) as f:
            geojson_data = json.load(f)

        module = fake_gdal(returns=MagicMock())
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("d2spy.extras.geo.gdal", module):
                geo.clip_by_mask(
                    in_raster, geojson_data, os.path.join(tmp_dir, "clip.tif")
                )
            module.BuildVRT.assert_not_called()
