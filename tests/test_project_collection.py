from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.project import Project
from d2spy.models.project_collection import ProjectCollection

from example_data import TEST_PROJECT


class TestProjectCollection(TestCase):
    def setUp(self):
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(base_url, session)

    def test_filter_by_description(self):
        collection = ProjectCollection(
            collection=[
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "Contains keyword"},
                ),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "Contains KEYWORD"},
                ),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "Contains Keyword!"},
                ),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "Shouldn't be selected"},
                ),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "Shouldn't be selected"},
                ),
            ]
        )

        filtered_collection = collection.filter_by_description("keyword")

        self.assertIsInstance(filtered_collection, ProjectCollection)
        self.assertEqual(len(filtered_collection), 3)
        for project in filtered_collection:
            self.assertIsInstance(project, Project)

    def test_filter_by_title(self):
        collection = ProjectCollection(
            collection=[
                Project(self.client, **{**TEST_PROJECT, "title": "Contains keyword"}),
                Project(self.client, **{**TEST_PROJECT, "title": "Contains KEYWORD"}),
                Project(self.client, **{**TEST_PROJECT, "title": "Contains Keyword!"}),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "title": "Shouldn't be selected"},
                ),
                Project(
                    self.client,
                    **{**TEST_PROJECT, "title": "Shouldn't be selected"},
                ),
            ]
        )

        filtered_collection = collection.filter_by_title("keyword")

        self.assertIsInstance(filtered_collection, ProjectCollection)
        self.assertEqual(len(filtered_collection), 3)
        for project in filtered_collection:
            self.assertIsInstance(project, Project)

    def test_filter_no_match(self):
        collection = ProjectCollection(
            collection=[
                Project(
                    self.client,
                    **{**TEST_PROJECT, "description": "No match here"},
                ),
            ]
        )

        filtered = collection.filter_by_description("nonexistent")
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, ProjectCollection)

    def test_empty_collection(self):
        collection = ProjectCollection()

        self.assertEqual(len(collection), 0)

        filtered = collection.filter_by_title("anything")
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, ProjectCollection)
