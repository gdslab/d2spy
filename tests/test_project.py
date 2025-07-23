from datetime import date
from typing import Dict, List
from unittest import TestCase
from unittest.mock import patch

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.flight import Flight
from d2spy.models.flight_collection import FlightCollection
from d2spy.models.project import Project

from example_data import (
    TEST_FEATURE_COLLECTION,
    TEST_MAP_LAYER,
    TEST_MULTI_PROJECT,
    TEST_PROJECT,
)


class TestProject(TestCase):
    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_add_flight(self, mock_make_post_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test project data
        project_id = TEST_PROJECT["id"]
        project = Project(client, **TEST_PROJECT)

        # User ID for pilot
        pilot_id = "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5"

        # Test flight data
        flight_data = {
            "acquisition_date": date.today(),
            "altitude": 40,
            "side_overlap": 85,
            "forward_overlap": 85,
            "sensor": "RGB",
            "platform": "M350",
            "name": "Test Flight",
            "pilot_id": pilot_id,
        }

        # Mock response from the POST request to create new flight
        mock_response_data = {
            "acquisition_date": str(date.today()),
            "altitude": flight_data["altitude"],
            "side_overlap": flight_data["side_overlap"],
            "forward_overlap": flight_data["forward_overlap"],
            "sensor": flight_data["sensor"],
            "platform": flight_data["platform"],
            "name": flight_data["name"],
            "is_active": True,
            "pilot_id": pilot_id,
            "id": "b4eb23cc-3d36-4586-b11c-a0a95b00d245",
            "deactivated_at": None,
            "read_only": False,
            "project_id": project_id,
            "data_products": [],
        }
        mock_make_post_request.return_value = mock_response_data

        # Add a flight to the project
        flight = project.add_flight(**flight_data)

        # Assert that the correct URL and JSON payload was used in the POST request
        mock_make_post_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights",
            json={
                **flight_data,
                # serialize date
                "acquisition_date": str(flight_data["acquisition_date"]),
            },
        )

        # Assert that the response data matches the test flight data
        self.assertIsInstance(flight, Flight)
        self.assertEqual(flight.acquisition_date, str(flight_data["acquisition_date"]))
        self.assertEqual(flight.altitude, flight_data["altitude"])
        self.assertEqual(flight.side_overlap, flight_data["side_overlap"])
        self.assertEqual(flight.forward_overlap, flight_data["forward_overlap"])
        self.assertEqual(flight.sensor, flight_data["sensor"])
        self.assertEqual(flight.platform, flight_data["platform"])
        self.assertEqual(flight.name, flight_data["name"])
        self.assertEqual(flight.pilot_id, flight_data["pilot_id"])

    @patch("d2spy.api_client.APIClient.make_post_request")
    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_add_flight_get_pilot(self, mock_make_get_request, mock_make_post_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)

        # Mock response from the GET request for current user model
        mock_response_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_email_confirmed": True,
            "is_approved": True,
            "id": "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5",
            "created_at": "2024-04-30T23:19:19.121688",
            "api_access_token": None,
            "exts": [],
            "is_superuser": False,
            "profile_url": (
                "http://example.com/static/users/dd18a0ea-d6fe-49e2-b16b-"
                "cb0faa7548b5/4abeedc1-91c2-48c5-8def-a28017bd9289.png"
            ),
        }
        mock_make_get_request.return_value = mock_response_data

        # Test flight data without a pilot ID
        flight_data = {
            "acquisition_date": date.today(),
            "altitude": 40,
            "side_overlap": 85,
            "forward_overlap": 85,
            "sensor": "RGB",
            "platform": "M350",
            "name": "Test Flight",
        }

        # Add a test flight to the test project
        project.add_flight(**flight_data)

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with("/api/v1/users/current")

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_flight(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)
        project_id = project.id

        # Test flight
        flight_data = {
            "acquisition_date": str(date.today()),
            "altitude": 40,
            "side_overlap": 85,
            "forward_overlap": 85,
            "sensor": "RGB",
            "platform": "M350",
            "name": "Test Flight",
            "pilot_id": "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5",
        }
        flight_id = "b4eb23cc-3d36-4586-b11c-a0a95b00d245"

        # Mock response for the GET request for an existing flight
        mock_response_data = {
            "acquisition_date": flight_data["acquisition_date"],
            "altitude": flight_data["altitude"],
            "side_overlap": flight_data["side_overlap"],
            "forward_overlap": flight_data["forward_overlap"],
            "sensor": flight_data["sensor"],
            "platform": flight_data["platform"],
            "name": flight_data["name"],
            "is_active": True,
            "pilot_id": flight_data["pilot_id"],
            "id": flight_id,
            "deactivated_at": None,
            "read_only": False,
            "project_id": project_id,
            "data_products": [],
        }
        mock_make_get_request.return_value = mock_response_data

        # Get a flight using its unique flight ID
        flight = project.get_flight(flight_id)

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights/{flight_id}"
        )

        # Assert that the response data matches the test flight data
        self.assertIsInstance(flight, Flight)
        self.assertEqual(flight.acquisition_date, flight_data["acquisition_date"])
        self.assertEqual(flight.altitude, flight_data["altitude"])
        self.assertEqual(flight.side_overlap, flight_data["side_overlap"])
        self.assertEqual(flight.forward_overlap, flight_data["forward_overlap"])
        self.assertEqual(flight.sensor, flight_data["sensor"])
        self.assertEqual(flight.platform, flight_data["platform"])
        self.assertEqual(flight.name, flight_data["name"])
        self.assertEqual(flight.pilot_id, flight_data["pilot_id"])

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_flights(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)
        project_id = project.id

        # Test flight
        flight_data = {
            "acquisition_date": str(date.today()),
            "altitude": 40,
            "side_overlap": 85,
            "forward_overlap": 85,
            "sensor": "RGB",
            "platform": "M350",
            "name": "Test Flight",
            "pilot_id": "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5",
        }
        flight_id = "b4eb23cc-3d36-4586-b11c-a0a95b00d245"

        # Mock response from the GET request for multiple flights
        mock_response_data = [
            {
                "acquisition_date": flight_data["acquisition_date"],
                "altitude": flight_data["altitude"],
                "side_overlap": flight_data["side_overlap"],
                "forward_overlap": flight_data["forward_overlap"],
                "sensor": flight_data["sensor"],
                "platform": flight_data["platform"],
                "name": flight_data["name"],
                "is_active": True,
                "pilot_id": flight_data["pilot_id"],
                "id": flight_id,
                "deactivated_at": None,
                "read_only": False,
                "project_id": project_id,
                "data_products": [],
            }
        ] * 5  # Return five flights
        mock_make_get_request.return_value = mock_response_data

        # Get multiple flights
        flights = project.get_flights()

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/flights", params={"has_raster": False}
        )

        # Assert that the response data was a collection of five flight objects
        self.assertIsInstance(flights, FlightCollection)
        self.assertEqual(len(flights), 5)
        # Assert that the response flight data matches the test flight data
        for flight in flights:
            self.assertIsInstance(flight, Flight)
            self.assertEqual(flight.acquisition_date, flight_data["acquisition_date"])
            self.assertEqual(flight.altitude, flight_data["altitude"])
            self.assertEqual(flight.side_overlap, flight_data["side_overlap"])
            self.assertEqual(flight.forward_overlap, flight_data["forward_overlap"])
            self.assertEqual(flight.sensor, flight_data["sensor"])
            self.assertEqual(flight.platform, flight_data["platform"])
            self.assertEqual(flight.name, flight_data["name"])
            self.assertEqual(flight.pilot_id, flight_data["pilot_id"])

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_project_boundary(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_MULTI_PROJECT)

        # Mock response from the GET request for a project object
        mock_response_data = {**TEST_PROJECT}
        mock_make_get_request.return_value = mock_response_data

        # Fetch the project boundary for the project
        project_boundary = project.get_project_boundary()

        # Assert that the correct URL and JSON payload was used in the GET request
        mock_make_get_request.assert_called_once_with(f"/api/v1/projects/{project.id}")

        # Assert that the Project field attribute returns the project boundary
        self.assertEqual(project_boundary, TEST_PROJECT["field"])

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_add_map_layer(self, mock_make_post_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)
        project_id = project.id

        # Test map layer data - feature collection with two features
        map_layer_name = "test_map_layer"
        map_layer_feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"row": 1, "col": 1},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-86.944517485972483, 41.444077836565455, 0.0],
                                [-86.94450551488066, 41.444077830791521, 0.0],
                                [-86.94450552255509, 41.444068823253602, 0.0],
                                [-86.94451749364525, 41.444068829027536, 0.0],
                                [-86.944517485972483, 41.444077836565455, 0.0],
                            ]
                        ],
                    },
                },
                {
                    "type": "Feature",
                    "properties": {"row": 1, "col": 2},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-86.944493543788852, 41.444077825016343, 0.0],
                                [-86.944481572697043, 41.444077819239929, 0.0],
                                [-86.94448158037477, 41.44406881170201, 0.0],
                                [-86.94449355146493, 41.444068817478424, 0.0],
                                [-86.944493543788852, 41.444077825016343, 0.0],
                            ]
                        ],
                    },
                },
            ],
        }

        # Mock response from the POST request for creating a new map layer
        mock_response_data = TEST_MAP_LAYER
        mock_make_post_request.return_value = mock_response_data

        # Add map layer to project
        response_feature_collection = project.add_map_layer(
            feature_collection=map_layer_feature_collection, layer_name=map_layer_name
        )

        # Assert that the correct URL and JSON payload was used in the POST request
        mock_make_post_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/vector_layers",
            json={
                "layer_name": map_layer_name,
                "geojson": map_layer_feature_collection,
            },
        )
        print(response_feature_collection)
        # Assert that the response data matches the test flight data
        self.assertIsInstance(response_feature_collection, Dict)
        self.assertIn("type", response_feature_collection)
        self.assertEqual(response_feature_collection["type"], "FeatureCollection")
        self.assertIn("features", response_feature_collection)
        self.assertIsInstance(response_feature_collection["features"], List)
        self.assertEqual(len(response_feature_collection["features"]), 2)
        self.assertIn("metadata", response_feature_collection)
        self.assertIn("preview_url", response_feature_collection["metadata"])

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_map_layers(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)
        project_id = project.id

        # Mock response from the GET request for map layers
        # TEST_FEATURE_COLLECTION is a list of two feature collections
        mock_response_data = TEST_FEATURE_COLLECTION
        mock_make_get_request.return_value = mock_response_data

        # Fetch map layers for project
        map_layers = project.get_map_layers()

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}/vector_layers", params={"format": "json"}
        )

        # Assert that the correct project map layers were returned
        self.assertIsInstance(map_layers, List)
        self.assertEqual(len(map_layers), 2)
        for feature_collection in map_layers:
            self.assertIsInstance(feature_collection, Dict)
            self.assertIn("features", feature_collection)
            features = feature_collection["features"]
            self.assertIsInstance(features, List)
            self.assertEqual(len(features), 2)

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_update(self, mock_make_put_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate APIClient with test URL and test session
        client = APIClient(base_url, session)

        # Test project data
        project = Project(client, **TEST_PROJECT)
        project_id = TEST_PROJECT["id"]

        old_title = TEST_PROJECT["title"]
        new_title = old_title + " Updated"

        # Mock response from the PUT request for updating an existing project
        mock_response_data = {**TEST_PROJECT, "title": new_title}
        mock_make_put_request.return_value = mock_response_data

        # Update the existing project's title
        update_data = {"title": new_title}
        project.update(**update_data)

        # Assert that the correct URL and JSON payload were used in the PUT request
        mock_make_put_request.assert_called_once_with(
            f"/api/v1/projects/{project_id}", json=update_data
        )

        # Assert that the project object now has the new title
        self.assertEqual(project.title, new_title)
