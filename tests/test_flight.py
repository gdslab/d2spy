import os
import tempfile
from datetime import date
from typing import List
from unittest import TestCase
from unittest.mock import patch, Mock

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.data_product import DataProduct
from d2spy.models.flight import Flight
from d2spy.models.project import Project
from d2spy.models.raw_data import RawData
from d2spy.workspace import Workspace

from example_data import TEST_FLIGHT, TEST_PROJECT


class TestFlight(TestCase):
    @patch("requests.post")
    def test_add_data_product(self, mock_post):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        project_id = TEST_FLIGHT["project_id"]

        # Create temporary file for the data product
        with tempfile.NamedTemporaryFile(suffix=".tif") as temp_data_product:
            # Test data product
            data_type = "ortho"
            data_product = {"filepath": temp_data_product.name, "data_type": data_type}

            # Expected headers and cookies
            expected_cookies = {"access_token": client.session.cookies["access_token"]}
            expected_headers = {
                "Tus-Resumable": "1.0.0",
                "X-Project-ID": "24f77778-08d4-47d6-86a6-c6e32848370f",
                "X-Flight-ID": "b4eb23cc-3d36-4586-b11c-a0a95b00d245",
                "X-Data-Type": data_type,
                "Accept-Language": "en-US,en;q=0.5",
                "Origin": "https://example.com",
            }

            # Mock response from the POST request
            mock_post.return_value.status_code = 201
            mock_post.return_value.headers = {"location": "/"}

            # Upload data product to flight
            flight.add_data_product(**data_product)

            # Assert that the correct URL, cookies, and headers were used
            actual_url = mock_post.call_args[0][0]
            self.assertEqual(actual_url, f"{base_url}/files")

            self.assertIn("cookies", mock_post.call_args.kwargs)
            actual_cookies = mock_post.call_args.kwargs["cookies"]
            self.assertEqual(actual_cookies, expected_cookies)

            self.assertIn("headers", mock_post.call_args.kwargs)
            actual_headers = mock_post.call_args.kwargs["headers"]
            for header in expected_headers:
                self.assertEqual(actual_headers[header], expected_headers[header])

    @patch("requests.post")
    def test_add_raw_data(self, mock_post):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        project_id = TEST_FLIGHT["project_id"]

        # Create temporary file for the raw data
        with tempfile.NamedTemporaryFile(suffix=".zip") as temp_raw_data:
            # Test raw data
            data_type = "raw"
            raw_data = {"filepath": temp_raw_data.name}

            # Expected headers and cookies
            expected_cookies = {"access_token": client.session.cookies["access_token"]}
            expected_headers = {
                "Tus-Resumable": "1.0.0",
                "X-Project-ID": "24f77778-08d4-47d6-86a6-c6e32848370f",
                "X-Flight-ID": "b4eb23cc-3d36-4586-b11c-a0a95b00d245",
                "X-Data-Type": data_type,
                "Accept-Language": "en-US,en;q=0.5",
                "Origin": "https://example.com",
            }

            # Mock response from the POST request
            mock_post.return_value.status_code = 201
            mock_post.return_value.headers = {"location": "/"}

            # Upload data product to flight
            flight.add_raw_data(**raw_data)

            # Assert that the correct URL, cookies, and headers were used
            actual_url = mock_post.call_args[0][0]
            self.assertEqual(actual_url, f"{base_url}/files")

            self.assertIn("cookies", mock_post.call_args.kwargs)
            actual_cookies = mock_post.call_args.kwargs["cookies"]
            self.assertEqual(actual_cookies, expected_cookies)

            self.assertIn("headers", mock_post.call_args.kwargs)
            actual_headers = mock_post.call_args.kwargs["headers"]
            for header in expected_headers:
                self.assertEqual(actual_headers[header], expected_headers[header])

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_data_products(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        project_id = TEST_FLIGHT["project_id"]
        data_product_id = "2c2d5ce4-5611-4108-9f66-83ca51f5f52b"
        filepath = f"/static/projects/{project_id}/flights/{flight_id}/data_products/{data_product_id}/cbfc16d2-e038-4876-a412-aecb4d97e544.tif"

        # Test data product
        data_type = "dsm"
        data_product_data = {
            "filepath": "/path/to/220604_dsm_rgb.tif",
            "data_type": data_type,
        }

        # Mock response from the GET request for multiple data products
        mock_response_data = [
            {
                "data_type": data_type,
                "filepath": filepath,
                "original_filename": os.path.basename(data_product_data["filepath"]),
                "stac_properties": {
                    "raster": [
                        {
                            "data_type": "float32",
                            "stats": {
                                "minimum": 187.849,
                                "maximum": 188.088,
                                "mean": 187.959,
                                "stddev": 0.038,
                            },
                            "nodata": None,
                        }
                    ],
                    "eo": [{"name": "b1", "description": "Gray"}],
                },
                "is_active": True,
                "is_initial_processing_completed": True,
                "id": data_product_id,
                "flight_id": flight_id,
                "user_style": {
                    "max": 188.088,
                    "min": 187.849,
                    "mode": "minMax",
                    "userMax": 188.088,
                    "userMin": 187.849,
                    "colorRamp": "rainbow",
                    "meanStdDev": 2,
                },
                "deactivated_at": None,
                "public": False,
                "status": "SUCCESS",
                "url": f"{base_url}/{filepath}",
            }
        ] * 5  # Return five data products
        mock_make_get_request.return_value = mock_response_data

        # Get multiple data products
        data_products = flight.get_data_products()

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights/{flight_id}/data_products"
        )

        # Assert that the response data was a list of five data products
        self.assertIsInstance(data_products, List)
        self.assertEqual(len(data_products), 5)
        # Assert that the response data product matches the original data product
        for data_product in data_products:
            self.assertIsInstance(data_product, DataProduct)
            self.assertEqual(data_product.data_type, data_product_data["data_type"])
            self.assertEqual(
                data_product.original_filename,
                os.path.basename(data_product_data["filepath"]),
            )

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_raw_data(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        project_id = TEST_FLIGHT["project_id"]
        raw_data_id = "218e24e8-fe2e-4892-a771-6440a949c459"
        filepath = f"/static/projects/{project_id}/flights/{flight_id}/raw_data/{raw_data_id}/d9b09d73-832d-48aa-8c51-ba8a25cf3dff.zip"

        # Test data product
        data_type = "raw"
        raw_data_test_data = {"filepath": "/path/to/test_raw_data.zip"}

        # Mock response from the GET request for multiple raw data zips
        mock_response_data = [
            {
                "filepath": filepath,
                "original_filename": os.path.basename(raw_data_test_data["filepath"]),
                "is_active": True,
                "is_initial_processing_completed": True,
                "id": raw_data_id,
                "flight_id": flight_id,
                "deactivated_at": None,
                "has_active_job": False,
                "status": "SUCCESS",
                "url": f"{base_url}/{filepath}",
            }
        ] * 5  # Return five raw data zips
        mock_make_get_request.return_value = mock_response_data

        # Get multiple raw data zips
        raw_data_datasets = flight.get_raw_data()

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights/{flight_id}/raw_data"
        )

        # Assert that the response data was a list of raw data zips
        self.assertIsInstance(raw_data_datasets, List)
        self.assertEqual(len(raw_data_datasets), 5)
        # Assert that the response raw data matches the original raw data
        for raw_data in raw_data_datasets:
            self.assertIsInstance(raw_data, RawData)
            self.assertEqual(
                raw_data.original_filename,
                os.path.basename(raw_data_test_data["filepath"]),
            )

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_move_project(self, mock_make_put_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        src_project = Project(client, **TEST_PROJECT)
        dst_project = Project(
            client, **{**TEST_PROJECT, "id": "383d041b-e72c-47fd-9ba1-dbd0985b9d04"}
        )
        # Source project and destination project must have different IDs
        self.assertNotEqual(src_project.id, dst_project.id)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        # Test flight's project ID should match src_project's ID
        self.assertEqual(flight.project_id, src_project.id)

        # Mock response from the PUT request for moving a flight
        mock_response_data = {**TEST_FLIGHT, "project_id": dst_project.id}
        mock_make_put_request.return_value = mock_response_data

        # Move the flight from src_project to dst_project
        flight.move_to_project(dst_project.id)

        # Assert that the correct URL and JSON payload was used in the PUT request
        mock_make_put_request.assert_called_once_with(
            f"/api/v1/projects/{src_project.id}/flights/{flight_id}/move_to_project/{dst_project.id}"
        )

        # Assert that the flight object now has the new platform
        self.assertEqual(flight.project_id, dst_project.id)

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_update(self, mock_make_put_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test flight data
        flight = Flight(client, **TEST_FLIGHT)
        flight_id = TEST_FLIGHT["id"]
        project_id = TEST_FLIGHT["project_id"]

        old_platform = TEST_FLIGHT["platform"]  # M350
        new_platform = "M300"

        # Mock response from the PUT request for updating an existing project
        mock_response_data = {**TEST_FLIGHT, "platform": new_platform}
        mock_make_put_request.return_value = mock_response_data

        # Update the existing flight's platform
        update_data = {"platform": new_platform}
        flight.update(**update_data)

        # Assert that the correct URL and JSON payload was used in the PUT request
        mock_make_put_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights/{flight_id}", json=update_data
        )

        # Assert that the flight object now has the new platform
        self.assertEqual(flight.platform, new_platform)
