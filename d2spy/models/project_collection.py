from typing import List

from d2spy.models.project import Project


class ProjectCollection:
    """Collection of Data to Science projects."""

    def __init__(self, collection: List[Project] = []):
        self.collection = collection

    def __getitem__(self, index: int) -> Project:
        return self.collection[int(index)]

    def __len__(self) -> int:
        return len(self.collection)

    def __repr__(self) -> str:
        return f"ProjectCollection({self.collection})"

    def filter_by_description(self, keyword: str) -> "ProjectCollection":
        """Returns list of projects with descriptions containing text that matches
        the keyword text.

        Args:
            keyword (str): Keyword text that will be matched with project descriptions.

        Returns:
            ProjectCollection: Collection of projects with keyword matches.
        """
        filtered_collection = [
            project
            for project in self.collection
            if keyword.lower() in project.description.lower()
        ]
        return ProjectCollection(collection=filtered_collection)

    def filter_by_title(self, keyword: str) -> "ProjectCollection":
        """Returns list of projects with titles containing text that matches
        the keyword text.

        Args:
            keyword (str): Keyword text that will be matched with project titles.

        Returns:
            List[Project]: List of projects with keyword matches.
        """
        filtered_collection = [
            project
            for project in self.collection
            if keyword.lower() in project.title.lower()
        ]
        return ProjectCollection(collection=filtered_collection)
