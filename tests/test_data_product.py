import os
import tempfile
from typing import List
from unittest import TestCase
from unittest.mock import patch

from geojson_pydantic import FeatureCollection
from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.data_product import DataProduct

from example_data import TEST_DATA_PRODUCT


class TestDataProduct(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Setup a test session
        self.base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        self.client = APIClient(self.base_url, session)

    def test_init(self):
        """Test DataProduct initialization"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        # Assert that all attributes are set correctly
        self.assertEqual(data_product.id, TEST_DATA_PRODUCT["id"])
        self.assertEqual(data_product.data_type, TEST_DATA_PRODUCT["data_type"])
        self.assertEqual(data_product.filepath, TEST_DATA_PRODUCT["filepath"])
        self.assertEqual(
            data_product.original_filename, TEST_DATA_PRODUCT["original_filename"]
        )
        self.assertEqual(data_product.is_active, TEST_DATA_PRODUCT["is_active"])
        self.assertEqual(data_product.flight_id, TEST_DATA_PRODUCT["flight_id"])
        self.assertEqual(data_product.public, TEST_DATA_PRODUCT["public"])
        self.assertEqual(
            data_product.stac_properties, TEST_DATA_PRODUCT["stac_properties"]
        )
        self.assertEqual(data_product.status, TEST_DATA_PRODUCT["status"])
        self.assertEqual(data_product.url, TEST_DATA_PRODUCT["url"])
        self.assertEqual(data_product.client, self.client)

    def test_repr(self):
        """Test DataProduct string representation"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        repr_string = repr(data_product)

        # Assert that the representation contains key information
        self.assertIn("DataProduct", repr_string)
        self.assertIn(f"data_type={TEST_DATA_PRODUCT['data_type']!r}", repr_string)
        self.assertIn(f"filepath={TEST_DATA_PRODUCT['filepath']!r}", repr_string)
        self.assertIn(
            f"original_filename={TEST_DATA_PRODUCT['original_filename']!r}",
            repr_string,
        )

    def test_get_band_info(self):
        """Test getting band information from data product"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        band_info = data_product.get_band_info()

        # Assert that band info is returned correctly
        self.assertIsNotNone(band_info)
        self.assertIsInstance(band_info, List)
        self.assertEqual(len(band_info), 1)
        self.assertEqual(band_info[0]["name"], "b1")
        self.assertEqual(band_info[0]["description"], "Gray")

    def test_get_band_info_point_cloud(self):
        """Test that get_band_info returns None for point clouds"""
        point_cloud_data = {**TEST_DATA_PRODUCT, "data_type": "point_cloud"}
        data_product = DataProduct(self.client, **point_cloud_data)

        band_info = data_product.get_band_info()

        # Assert that None is returned for point clouds
        self.assertIsNone(band_info)

    def test_get_band_info_missing_eo(self):
        """Test get_band_info when eo properties are missing"""
        data_without_eo = {
            **TEST_DATA_PRODUCT,
            "stac_properties": {
                "raster": TEST_DATA_PRODUCT["stac_properties"]["raster"]
            },
        }
        data_product = DataProduct(self.client, **data_without_eo)

        band_info = data_product.get_band_info()

        # Assert that None is returned when eo properties are missing
        self.assertIsNone(band_info)

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_update_band_info(self, mock_make_put_request):
        """Test updating band information"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"
        flight_id = TEST_DATA_PRODUCT["flight_id"]
        data_product_id = TEST_DATA_PRODUCT["id"]

        # New band info to update
        new_band_info = [{"name": "b1", "description": "Updated Gray Band"}]

        # Mock response from the PUT request
        updated_stac_properties = {
            **TEST_DATA_PRODUCT["stac_properties"],
            "eo": new_band_info,
        }
        mock_response_data = {
            **TEST_DATA_PRODUCT,
            "stac_properties": updated_stac_properties,
        }
        mock_make_put_request.return_value = mock_response_data

        # Update band info
        result = data_product.update_band_info(new_band_info)

        # Assert that the correct URL and JSON payload was used in the PUT request
        expected_endpoint = (
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
            f"/data_products/{data_product_id}/bands"
        )
        mock_make_put_request.assert_called_once_with(
            expected_endpoint, json={"bands": new_band_info}
        )

        # Assert that the updated band info is returned
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["description"], "Updated Gray Band")

        # Assert that the data product object was updated
        self.assertEqual(
            data_product.stac_properties["eo"][0]["description"], "Updated Gray Band"
        )

    def test_update_band_info_no_project_id(self):
        """Test update_band_info when project ID cannot be found"""
        # Create data product with URL that doesn't contain project ID
        data_without_project = {
            **TEST_DATA_PRODUCT,
            "url": "https://example.com/invalid/url",
        }
        data_product = DataProduct(self.client, **data_without_project)

        new_band_info = [{"name": "b1", "description": "Updated Gray Band"}]
        result = data_product.update_band_info(new_band_info)

        # Assert that None is returned when project ID cannot be found
        self.assertIsNone(result)

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_derive_ndvi(self, mock_make_post_request):
        """Test deriving NDVI data product"""
        # Create data product with multiple bands
        multi_band_data = {
            **TEST_DATA_PRODUCT,
            "stac_properties": {
                **TEST_DATA_PRODUCT["stac_properties"],
                "eo": [
                    {"name": "b1", "description": "Red"},
                    {"name": "b2", "description": "Green"},
                    {"name": "b3", "description": "NIR"},
                ],
            },
        }
        data_product = DataProduct(self.client, **multi_band_data)

        red_band_idx = 1
        nir_band_idx = 3

        # Mock response from the POST request
        mock_make_post_request.return_value = {}

        # Derive NDVI
        result = data_product.derive_ndvi(red_band_idx, nir_band_idx)

        # Assert that the job was submitted successfully
        self.assertTrue(result)

        # Extract expected endpoint
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"
        flight_id = TEST_DATA_PRODUCT["flight_id"]
        data_product_id = TEST_DATA_PRODUCT["id"]
        expected_endpoint = (
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
            f"/data_products/{data_product_id}/tools"
        )

        # Verify the API call was made with correct parameters
        mock_make_post_request.assert_called_once()
        call_args = mock_make_post_request.call_args
        self.assertEqual(call_args[0][0], expected_endpoint)
        self.assertTrue(call_args[1]["json"]["ndvi"])
        self.assertEqual(call_args[1]["json"]["ndviRed"], red_band_idx)
        self.assertEqual(call_args[1]["json"]["ndviNIR"], nir_band_idx)

    def test_derive_ndvi_point_cloud(self):
        """Test that derive_ndvi returns False for point clouds"""
        point_cloud_data = {**TEST_DATA_PRODUCT, "data_type": "point_cloud"}
        data_product = DataProduct(self.client, **point_cloud_data)

        result = data_product.derive_ndvi(1, 2)

        # Assert that False is returned for point clouds
        self.assertFalse(result)

    def test_derive_ndvi_insufficient_bands(self):
        """Test derive_ndvi with insufficient bands"""
        # Data product with only one band
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        result = data_product.derive_ndvi(1, 2)

        # Assert that False is returned when there are insufficient bands
        self.assertFalse(result)

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_derive_exg(self, mock_make_post_request):
        """Test deriving Excess Green Index data product"""
        # Create data product with multiple bands
        multi_band_data = {
            **TEST_DATA_PRODUCT,
            "stac_properties": {
                **TEST_DATA_PRODUCT["stac_properties"],
                "eo": [
                    {"name": "b1", "description": "Red"},
                    {"name": "b2", "description": "Green"},
                    {"name": "b3", "description": "Blue"},
                ],
            },
        }
        data_product = DataProduct(self.client, **multi_band_data)

        red_band_idx = 1
        green_band_idx = 2
        blue_band_idx = 3

        # Mock response from the POST request
        mock_make_post_request.return_value = {}

        # Derive ExG
        result = data_product.derive_exg(red_band_idx, green_band_idx, blue_band_idx)

        # Assert that the job was submitted successfully
        self.assertTrue(result)

        # Extract expected endpoint
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"
        flight_id = TEST_DATA_PRODUCT["flight_id"]
        data_product_id = TEST_DATA_PRODUCT["id"]
        expected_endpoint = (
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
            f"/data_products/{data_product_id}/tools"
        )

        # Verify the API call was made with correct parameters
        mock_make_post_request.assert_called_once()
        call_args = mock_make_post_request.call_args
        self.assertEqual(call_args[0][0], expected_endpoint)
        self.assertTrue(call_args[1]["json"]["exg"])
        self.assertEqual(call_args[1]["json"]["exgRed"], red_band_idx)
        self.assertEqual(call_args[1]["json"]["exgGreen"], green_band_idx)
        self.assertEqual(call_args[1]["json"]["exgBlue"], blue_band_idx)

    def test_derive_exg_point_cloud(self):
        """Test that derive_exg returns False for point clouds"""
        point_cloud_data = {**TEST_DATA_PRODUCT, "data_type": "point_cloud"}
        data_product = DataProduct(self.client, **point_cloud_data)

        result = data_product.derive_exg(1, 2, 3)

        # Assert that False is returned for point clouds
        self.assertFalse(result)

    def test_derive_exg_insufficient_bands(self):
        """Test derive_exg with insufficient bands"""
        # Data product with only one band
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        result = data_product.derive_exg(1, 2, 3)

        # Assert that False is returned when there are insufficient bands
        self.assertFalse(result)

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_generate_zonal_statistics(self, mock_make_post_request):
        """Test generating zonal statistics"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        zonal_layer_id = "test_layer_id"

        # Mock response from the POST request
        mock_make_post_request.return_value = {}

        # Generate zonal statistics
        result = data_product.generate_zonal_statistics(zonal_layer_id)

        # Assert that the job was submitted successfully
        self.assertTrue(result)

        # Extract expected endpoint
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"
        flight_id = TEST_DATA_PRODUCT["flight_id"]
        data_product_id = TEST_DATA_PRODUCT["id"]
        expected_endpoint = (
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
            f"/data_products/{data_product_id}/tools"
        )

        # Verify the API call was made with correct parameters
        mock_make_post_request.assert_called_once()
        call_args = mock_make_post_request.call_args
        self.assertEqual(call_args[0][0], expected_endpoint)
        self.assertEqual(call_args[1]["json"]["zonal_layer_id"], zonal_layer_id)
        self.assertEqual(call_args[1]["json"]["dem_id"], str(data_product_id))

    def test_generate_zonal_statistics_no_project_id(self):
        """Test generate_zonal_statistics when project ID cannot be found"""
        # Create data product with URL that doesn't contain project ID
        data_without_project = {
            **TEST_DATA_PRODUCT,
            "url": "https://example.com/invalid/url",
        }
        data_product = DataProduct(self.client, **data_without_project)

        result = data_product.generate_zonal_statistics("test_layer_id")

        # Assert that False is returned when project ID cannot be found
        self.assertFalse(result)

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_zonal_statistics_existing(self, mock_make_get_request):
        """Test getting existing zonal statistics"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        zonal_layer_id = "test_layer_id"

        # Mock response with existing zonal statistics
        mock_response_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-86.944517486, 41.444077837],
                                [-86.944505515, 41.444077831],
                                [-86.944505523, 41.444068823],
                                [-86.944517494, 41.444068829],
                                [-86.944517486, 41.444077837],
                            ]
                        ],
                    },
                    "properties": {"mean": 187.95, "std": 0.038},
                }
            ],
        }
        mock_make_get_request.return_value = mock_response_data

        # Get zonal statistics (should return immediately since they exist)
        result = data_product.get_zonal_statistics(zonal_layer_id, wait=False)

        # Assert that the feature collection is returned
        self.assertIsNotNone(result)
        self.assertIsInstance(result, FeatureCollection)
        self.assertEqual(len(result.features), 1)

        # Extract expected endpoint
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"
        flight_id = TEST_DATA_PRODUCT["flight_id"]
        data_product_id = TEST_DATA_PRODUCT["id"]
        expected_endpoint = (
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
            f"/data_products/{data_product_id}/zonal_statistics"
        )

        # Verify the API call was made
        mock_make_get_request.assert_called_once_with(
            f"{expected_endpoint}?layer_id={zonal_layer_id}"
        )

    @patch("d2spy.api_client.APIClient.make_post_request")
    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_zonal_statistics_not_existing_no_wait(
        self, mock_make_get_request, mock_make_post_request
    ):
        """Test getting zonal statistics that don't exist without waiting"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        zonal_layer_id = "test_layer_id"

        # Mock response with no existing statistics
        mock_make_get_request.return_value = None
        mock_make_post_request.return_value = {}

        # Get zonal statistics without waiting
        result = data_product.get_zonal_statistics(zonal_layer_id, wait=False)

        # Assert that None is returned when not waiting
        self.assertIsNone(result)

        # Verify that a job was submitted
        mock_make_post_request.assert_called_once()

    @patch("time.sleep", return_value=None)
    @patch("d2spy.api_client.APIClient.make_post_request")
    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_zonal_statistics_not_existing_with_wait(
        self, mock_make_get_request, mock_make_post_request, mock_sleep
    ):
        """Test getting zonal statistics that don't exist with polling"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        zonal_layer_id = "test_layer_id"

        # Mock response: first call returns None, second call returns data
        mock_response_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-86.944517486, 41.444077837],
                                [-86.944505515, 41.444077831],
                                [-86.944505523, 41.444068823],
                                [-86.944517494, 41.444068829],
                                [-86.944517486, 41.444077837],
                            ]
                        ],
                    },
                    "properties": {"mean": 187.95, "std": 0.038},
                }
            ],
        }
        mock_make_get_request.side_effect = [None, mock_response_data]
        mock_make_post_request.return_value = {}

        # Get zonal statistics with waiting
        result = data_product.get_zonal_statistics(
            zonal_layer_id, wait=True, timeout=300, poll_interval=5
        )

        # Assert that the feature collection is eventually returned
        self.assertIsNotNone(result)
        self.assertIsInstance(result, FeatureCollection)
        self.assertEqual(len(result.features), 1)

        # Verify that polling occurred
        self.assertEqual(mock_make_get_request.call_count, 2)
        mock_sleep.assert_called()

    def test_get_zonal_statistics_point_cloud(self):
        """Test that get_zonal_statistics returns None for point clouds"""
        point_cloud_data = {**TEST_DATA_PRODUCT, "data_type": "point_cloud"}
        data_product = DataProduct(self.client, **point_cloud_data)

        result = data_product.get_zonal_statistics("test_layer_id")

        # Assert that None is returned for point clouds
        self.assertIsNone(result)

    def test_get_zonal_statistics_multiple_bands(self):
        """Test that get_zonal_statistics returns None for multi-band rasters"""
        # Create data product with multiple bands
        multi_band_data = {
            **TEST_DATA_PRODUCT,
            "stac_properties": {
                **TEST_DATA_PRODUCT["stac_properties"],
                "eo": [
                    {"name": "b1", "description": "Red"},
                    {"name": "b2", "description": "Green"},
                ],
            },
        }
        data_product = DataProduct(self.client, **multi_band_data)

        result = data_product.get_zonal_statistics("test_layer_id")

        # Assert that None is returned for multi-band rasters
        self.assertIsNone(result)

    @patch("d2spy.models.data_product.clip_by_mask")
    def test_clip(self, mock_clip_by_mask):
        """Test clipping data product by GeoJSON"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        # Create a temporary output raster path
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_file:
            out_raster = temp_file.name

        try:
            # GeoJSON feature for clipping
            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.944517486, 41.444077837],
                            [-86.944505515, 41.444077831],
                            [-86.944505523, 41.444068823],
                            [-86.944517494, 41.444068829],
                            [-86.944517486, 41.444077837],
                        ]
                    ],
                },
                "properties": {},
            }

            # Mock the clip_by_mask function
            mock_clip_by_mask.return_value = None

            # Clip the data product
            result = data_product.clip(geojson_feature, out_raster)

            # Assert that clipping was successful
            self.assertTrue(result)

            # Verify that clip_by_mask was called with correct parameters
            mock_clip_by_mask.assert_called_once_with(
                data_product.url, geojson_feature, out_raster, False
            )
        finally:
            # Clean up the temporary file
            if os.path.exists(out_raster):
                os.remove(out_raster)

    def test_clip_point_cloud(self):
        """Test that clip returns False for point clouds"""
        point_cloud_data = {**TEST_DATA_PRODUCT, "data_type": "point_cloud"}
        data_product = DataProduct(self.client, **point_cloud_data)

        result = data_product.clip({}, "output.tif")

        # Assert that False is returned for point clouds
        self.assertFalse(result)

    @patch("d2spy.models.data_product.clip_by_mask")
    def test_clip_with_api_key(self, mock_clip_by_mask):
        """Test clipping with API key when 401 error occurs"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        # Create a temporary output raster path
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_file:
            out_raster = temp_file.name

        try:
            # GeoJSON feature for clipping
            geojson_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.944517486, 41.444077837],
                            [-86.944505515, 41.444077831],
                            [-86.944505523, 41.444068823],
                            [-86.944517494, 41.444068829],
                            [-86.944517486, 41.444077837],
                        ]
                    ],
                },
                "properties": {},
            }

            # Mock the clip_by_mask function to raise 401 error first, then succeed
            from rasterio.errors import RasterioIOError

            mock_clip_by_mask.side_effect = [
                RasterioIOError("HTTP response code: 401"),
                None,
            ]

            # Set API key in environment
            os.environ["D2S_API_KEY"] = "test_api_key"

            try:
                # Clip the data product
                result = data_product.clip(geojson_feature, out_raster)

                # Assert that clipping was successful
                self.assertTrue(result)

                # Verify that clip_by_mask was called twice
                self.assertEqual(mock_clip_by_mask.call_count, 2)
            finally:
                # Clean up environment variable
                del os.environ["D2S_API_KEY"]
        finally:
            # Clean up the temporary file
            if os.path.exists(out_raster):
                os.remove(out_raster)

    def test_get_default_tools_payload(self):
        """Test that default tools payload is correct"""
        data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)

        payload = data_product._get_default_tools_payload()

        # Assert that payload contains all expected keys
        self.assertIsInstance(payload, dict)
        self.assertIn("chm", payload)
        self.assertIn("dem_id", payload)
        self.assertIn("dtm", payload)
        self.assertIn("exg", payload)
        self.assertIn("hillshade", payload)
        self.assertIn("ndvi", payload)
        self.assertIn("vari", payload)
        self.assertIn("zonal", payload)
        self.assertIn("zonal_layer_id", payload)

        # Assert that default values are correct
        self.assertFalse(payload["chm"])
        self.assertFalse(payload["dtm"])
        self.assertFalse(payload["exg"])
        self.assertFalse(payload["hillshade"])
        self.assertFalse(payload["ndvi"])
        self.assertFalse(payload["vari"])
        self.assertTrue(payload["zonal"])
