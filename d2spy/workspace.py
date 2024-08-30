import requests
from datetime import datetime
from typing import Optional

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.auth import Auth
from d2spy.extras.utils import ensure_dict, ensure_list_of_dict
from d2spy.models.project_collection import ProjectCollection


class Workspace:
    """Create and view projects on D2S instance."""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

        self.client = APIClient(self.base_url, self.session)

    @classmethod
    def connect(cls, base_url: str, email: str) -> "Workspace":
        """Login and create workspace.

        Args:
            base_url (str): Base URL for D2S instance.
            email (str): Email address used to sign in to D2S.

        Returns:
            Workspace: D2S workspace for creating and viewing data.
        """
        auth = Auth(base_url)
        auth.login(email=email)

        return cls(base_url, auth.session)

    def logout(self) -> None:
        """Logout of D2S platform."""
        # Delete access-token cookie from session and end session
        self.session.cookies.clear(domain="", path="/", name="access_token")
        self.session.close()
        print("session ended")

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
            planting_date (Optional[datetime]): Planting date. Defaults to None.
            harvest_date (Optional[datetime]): Harvest date. Defaults to None.

        Returns:
            models.Project: New project instance.
        """
        endpoint = "/api/v1/projects"
        data = {
            "title": title,
            "description": description,
            "location": location,
            "planting_date": planting_date,
            "harvest_date": harvest_date,
        }

        response_data = self.client.make_post_request(endpoint, json=data)
        project = schemas.Project.from_dict(response_data)
        return models.Project(self.client, **project.__dict__)

    def get_project(self, project_id: str) -> Optional[models.Project]:
        """Request single project by ID. Project must be active and viewable by user.

        Args:
            project_id (str): Project ID.

        Returns:
            Optional[models.Project]: Project matching ID or None.
        """
        endpoint = f"/api/v1/projects/{project_id}"
        response_data = self.client.make_get_request(endpoint)
        response_data = ensure_dict(response_data)
        project = schemas.Project.from_dict(response_data)
        return models.Project(self.client, **project.__dict__)

    def get_projects(self, has_raster: Optional[bool] = False) -> ProjectCollection:
        """Request multiple projects. Only active projects viewable by
        user will be returned.

        Args:
            has_raster (Optional[bool], optional): Only return projects with rasters.

        Returns:
            ProjectCollection: Collection of all projects viewable by user.
        """
        endpoint = "/api/v1/projects"
        response_data = self.client.make_get_request(
            endpoint, params={"has_raster": has_raster}
        )
        response_data = ensure_list_of_dict(response_data)
        projects = [
            models.Project(
                self.client, **schemas.MultiProject.from_dict(project).__dict__
            )
            for project in response_data
        ]
        return ProjectCollection(collection=projects)
