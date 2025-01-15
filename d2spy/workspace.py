import os
import warnings
from datetime import date
from typing import Optional

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.auth import Auth
from d2spy.extras.utils import ensure_dict, ensure_list_of_dict
from d2spy.models.project_collection import ProjectCollection
from d2spy.schemas.session import D2SpySession


class Workspace:
    """Create and view projects on D2S instance."""

    def __init__(self, base_url: str, session: D2SpySession, api_key: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.session = session

        self.client = APIClient(self.base_url, self.session)

    @classmethod
    def connect(cls, base_url: str, email: Optional[str] = None) -> "Workspace":
        """Login and create workspace. If the email argument is not provided, the
        method will use the value of the D2S_EMAIL environment variable. If neither is
        available, an exception will be thrown.

        Args:
            base_url (str): Base URL for D2S instance.
            email Optional[str]: Email address used to sign in to D2S.

        Returns:
            Workspace: D2S workspace for creating and viewing data.
        """
        auth = Auth(base_url)

        # Check for email environment variable if not provided as argument
        if not email:
            email = os.environ.get("D2S_EMAIL")
            if not email:
                raise ValueError(
                    "Must provide 'email' to login method as argument or set email as "
                    "environment variable 'D2S_EMAIL'"
                )

        auth.login(email=email)

        # Set user api key if available
        if hasattr(auth.session, "d2s_data"):
            api_key = auth.session.d2s_data["API_KEY"]
        else:
            api_key = ""

        return cls(base_url, auth.session, api_key)

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
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        planting_date: Optional[date] = None,  # Deprecated
        harvest_date: Optional[date] = None,  # Deprecated
    ) -> models.Project:
        """Create new project in workspace.

        Args:
            title (str): Title for project.
            description (str): Description of project.
            location (dict): GeoJSON object representing location of project.
            start_date (Optional[date]): Start date of project. Defaults to None.
            end_date (Optional[date]): End date of project. Defaults to None.
            planting_date (Optional[date]): Planting date. Defaults to None. Deprecated.
            harvest_date (Optional[date]): Harvest date. Defaults to None. Deprecated.

        Returns:
            models.Project: New project instance.
        """
        if planting_date:
            warnings.warn(
                "'planting_date' is deprecated and will be removed in future versions.",
                DeprecationWarning,
                stacklevel=2,
            )
            start_date = start_date or planting_date

        start_date_serialized = (
            start_date.isoformat() if isinstance(start_date, date) else None
        )

        if harvest_date:
            warnings.warn(
                "'harvest_date' is deprecated and will be removed in future versions.",
                DeprecationWarning,
                stacklevel=2,
            )
            end_date = end_date or harvest_date

        end_date_serialized = (
            end_date.isoformat() if isinstance(end_date, date) else None
        )

        endpoint = "/api/v1/projects"
        data = {
            "title": title,
            "description": description,
            "location": location,
            "planting_date": start_date_serialized,
            "harvest_date": end_date_serialized,
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
