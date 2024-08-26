from datetime import datetime, timedelta
from typing import List
from unittest import TestCase
from unittest.mock import patch, Mock

from requests import Session

from d2spy.models.project import Project
from d2spy.workspace import Workspace
from example_data import TEST_PROJECT


class TestWorkspace(TestCase):
    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_add_project(self, mock_make_post_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the Workspace with a test URL and the test session
        workspace = Workspace(base_url, session)

        # Test project data
        project_data = {
            "title": "Test Project",
            "description": "Project for testing d2spy package.",
            "location": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [30.0, 10.0],
                            [40.0, 10.0],
                            [40.0, 20.0],
                            [30.0, 20.0],
                            [30.0, 10.0],
                        ]
                    ],
                },
            },
            "harvest_date": datetime.now(),
            "planting_date": datetime.now() - timedelta(days=90),
        }

        # Mock response from the POST request to create new project
        mock_response_data = {
            "title": project_data["title"],
            "description": project_data["description"],
            "planting_date": str(project_data["planting_date"]),
            "harvest_date": str(project_data["harvest_date"]),
            "location_id": "ad7aecdd-67d6-4fe5-b52b-52ba360f26aa",
            "team_id": None,
            "id": "24f77778-08d4-47d6-86a6-c6e32848370f",
            "is_active": True,
            "deactivated_at": None,
            "field": {
                **project_data["location"],
                "properties": {
                    "id": "ad7aecdd-67d6-4fe5-b52b-52ba360f26aa",
                    "center_x": 40,
                    "center_y": 20,
                },
            },
            "flight_count": 0,
            "most_recent_flight": None,
            "role": "owner",
        }
        mock_make_post_request.return_value = mock_response_data

        # Add a project to the workspace
        project = workspace.add_project(**project_data)

        # Assert that the correct URL and JSON payload was used in the POST request
        mock_make_post_request.assert_called_once_with(
            "/api/v1/projects",
            json=project_data,
        )

        # Assert that the response data matches the test project data
        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, project_data["title"])
        self.assertEqual(project.description, project_data["description"])
        self.assertEqual(project.planting_date, str(project_data["planting_date"]))
        self.assertEqual(project.harvest_date, str(project_data["harvest_date"]))

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_project(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the Workspace with a test URL and the test session
        workspace = Workspace(base_url, session)

        # Test project data
        project_data = {
            "title": "Test Project",
            "description": "Project for testing d2spy package.",
            "location": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [30.0, 10.0],
                            [40.0, 10.0],
                            [40.0, 20.0],
                            [30.0, 20.0],
                            [30.0, 10.0],
                        ]
                    ],
                },
            },
            "harvest_date": datetime.now(),
            "planting_date": datetime.now() - timedelta(days=90),
        }
        project_id = "24f77778-08d4-47d6-86a6-c6e32848370f"

        # Mock response from the GET request for an existing project
        mock_response_data = {
            "title": project_data["title"],
            "description": project_data["description"],
            "planting_date": str(project_data["planting_date"]),
            "harvest_date": str(project_data["harvest_date"]),
            "location_id": "ad7aecdd-67d6-4fe5-b52b-52ba360f26aa",
            "team_id": None,
            "id": "24f77778-08d4-47d6-86a6-c6e32848370f",
            "is_active": True,
            "deactivated_at": None,
            "field": {
                **project_data["location"],
                "properties": {
                    "id": "ad7aecdd-67d6-4fe5-b52b-52ba360f26aa",
                    "center_x": 40,
                    "center_y": 20,
                },
            },
            "flight_count": 0,
            "most_recent_flight": None,
            "role": "owner",
        }
        mock_make_get_request.return_value = mock_response_data

        # Get a project using its unique project ID
        project = workspace.get_project(project_id)

        # Assert that the correct URL was used in the GET request
        mock_make_get_request.assert_called_once_with(f"/api/v1/projects/{project_id}")

        # Assert that the response data matches the test project data
        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, project_data["title"])
        self.assertEqual(project.description, project_data["description"])
        self.assertEqual(project.planting_date, str(project_data["planting_date"]))
        self.assertEqual(project.harvest_date, str(project_data["harvest_date"]))

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_projects(self, mock_make_get_request):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the Workspace with a test URL and the test session
        workspace = Workspace(base_url, session)

        # Test project data
        project_data = {
            "id": "24f77778-08d4-47d6-86a6-c6e32848370f",
            "centroid": {"x": 40.0, "y": 20.0},
            "description": "Project for testing d2spy package.",
            "flight_count": 0,
            "role": "viewer",
            "title": "Project title",
        }

        # Mock response from the GET request for multiple projects
        mock_response_data = [project_data] * 5  # Return five copies of the project
        mock_make_get_request.return_value = mock_response_data

        # Get all of the projects accessible in the workspace
        projects = workspace.get_projects()

        # Assert that the correct URL and parameters were used in the GET request
        mock_make_get_request.assert_called_once_with(
            f"/api/v1/projects", params={"has_raster": False}
        )

        # Assert that the response data was a list of five project objects
        self.assertIsInstance(projects, List)
        self.assertEqual(len(projects), 5)
        # Assert that the response project data matches the test project data
        for project in projects:
            self.assertIsInstance(project, Project)
            self.assertEqual(project.title, project_data["title"])
            self.assertEqual(project.description, project_data["description"])
            self.assertEqual(project.flight_count, project_data["flight_count"])
            self.assertEqual(project.role, project_data["role"])
            self.assertEqual(project.centroid, project_data["centroid"])
