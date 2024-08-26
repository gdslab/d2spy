from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.project import Project
from d2spy.models.project_collection import ProjectCollection

from example_data import TEST_PROJECT


class TestProjectCollection(TestCase):
    def test_filter_by_description(self):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test project collection
        collection = ProjectCollection(
            collection=[
                Project(client, **{**TEST_PROJECT, "description": "Contains keyword"}),
                Project(client, **{**TEST_PROJECT, "description": "Contains KEYWORD"}),
                Project(client, **{**TEST_PROJECT, "description": "Contains Keyword!"}),
                Project(
                    client, **{**TEST_PROJECT, "description": "Shouldn't be selected"}
                ),
                Project(
                    client, **{**TEST_PROJECT, "description": "Shouldn't be selected"}
                ),
            ]
        )

        # Find projects with "keyword" in description
        filtered_collection = collection.filter_by_description("keyword")

        # filter_by_description should return new ProjectCollection with results
        self.assertIsInstance(filtered_collection, ProjectCollection)
        # Three project descriptions contain "keyword"
        self.assertEqual(len(filtered_collection), 3)
        # Each item in returned ProjectCollection should be Project
        for project in filtered_collection:
            self.assertIsInstance(project, Project)

    def test_filter_by_title(self):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test project collection
        collection = ProjectCollection(
            collection=[
                Project(client, **{**TEST_PROJECT, "title": "Contains keyword"}),
                Project(client, **{**TEST_PROJECT, "title": "Contains KEYWORD"}),
                Project(client, **{**TEST_PROJECT, "title": "Contains Keyword!"}),
                Project(client, **{**TEST_PROJECT, "title": "Shouldn't be selected"}),
                Project(client, **{**TEST_PROJECT, "title": "Shouldn't be selected"}),
            ]
        )

        # Find projects with "keyword" in title
        filtered_collection = collection.filter_by_title("keyword")

        # filter_by_title should return new ProjectCollection with results
        self.assertIsInstance(filtered_collection, ProjectCollection)
        # Three project titles contain "keyword"
        self.assertEqual(len(filtered_collection), 3)
        # Each item in returned ProjectCollection should be Project
        for project in filtered_collection:
            self.assertIsInstance(project, Project)
