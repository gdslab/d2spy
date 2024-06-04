import requests
from datetime import datetime
from typing import List, Optional

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.utils import pretty_print_response


class Workspace:
    """Create and view projects on D2S instance."""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

        self.client = APIClient(self.base_url, self.session)

    def add_project(
        self,
        title: str,
        description: str,
        location: dict,
        planting_date: Optional[datetime] = None,
        harvest_date: Optional[datetime] = None,
    ) -> models.Project:
        """Create new project in workspace.

        Args:
            title (str): Title for project.
            description (str): Description of project.
            location (dict): GeoJSON object representing location of project.
            planting_date (Optional[datetime]): Optional planting date. Defaults to None.
            harvest_date (Optional[datetime]): Optional harvest date. Defaults to None.

        Returns:
            models.Project: New project instance.
        """
        endpoint = f"/api/v1/projects"
        data = {
            "title": title,
            "description": description,
            "location": location,
            "planting_date": planting_date,
            "harvest_date": harvest_date,
        }

        response = self.client.make_post_request(endpoint, json=data)

        if response.status_code == 201:
            response_data = response.json()
            if response_data:
                project = schemas.Project.from_dict(response_data)
                return models.Project(self.client, **project.__dict__)

        pretty_print_response(response)
        return None

    def get_project(self, project_id: str) -> Optional[models.Project]:
        """Request single project by ID. Project must be active and viewable by user.

        Args:
            project_id (str): Project ID.

        Returns:
            Optional[models.Project]: Project matching ID or None.
        """
        endpoint = f"/api/v1/projects/{project_id}"
        response = self.client.make_get_request(endpoint)

        if response.status_code == 200:
            response_data: Union[dict, None] = response.json()
            if response_data:
                project = schemas.Project.from_dict(response_data)
                return models.Project(self.client, **project.__dict__)

        return None

    def get_projects(self) -> List[models.Project]:
        """Request multiple projects. Only active projects viewable by
        user will be returned.

        Returns:
            List[models.Project]: List of all projects viewable by user.
        """
        endpoint = "/api/v1/projects"
        response = self.client.make_get_request(endpoint)

        if response.status_code == 200:
            response_data: List[dict] = response.json()
            if len(response_data) > 0:
                projects = [
                    models.Project(
                        self.client, **schemas.Project.from_dict(project).__dict__
                    )
                    for project in response_data
                ]
                return projects

        pretty_print_response(response)
        return []
