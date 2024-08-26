from datetime import date, datetime
import json
import requests
from datetime import date
from typing import List, Literal, Optional, Union
from uuid import UUID

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.utils import pretty_print_response
from d2spy.models.flight_collection import FlightCollection
from d2spy.schemas.geojson import GeoJSON


class Project:
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # project attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"Project(title={self.title!r}, description={self.description!r})"

    def add_flight(
        self,
        acquisition_date: date,
        altitude: float,
        side_overlap: float,
        forward_overlap: float,
        sensor: Literal["RGB", "Multispectral", "LiDAR", "Other"],
        platform: Union[Literal["Phantom_4", "M300", "M350", "Other"], str],
        name: Optional[str] = None,
        pilot_id: Optional[UUID] = None,
    ) -> models.Flight:
        """Create new flight in a project.

        Args:
            name (Optional[str]): Name of flight.
            acquisition_date (date): Date of flight.
            altitude (float): Flight altitude.
            side_overlap (float): Flight side overlap %.
            forward_overlap (float): Flight forward overlap %.
            sensor (Literal["RGB", "Multispectral", "LiDAR", "Other"]): Sensor used for collecting data on flight.
            platform (Union[Literal["Phantom_4", "M300", "M350"], str]): Platform used for flight.
            pilot_id (Optional[UUID]): ID of the flight's pilot. Defaults to None.

        Returns:
            models.Flight: Newly created flight.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights"

        # if pilot id not provided, use current user's id
        if not pilot_id:
            user = self.client.make_get_request("/api/v1/users/current")
            pilot_id = user["id"]

        # Check if we need to serialize the acquisition date
        if isinstance(acquisition_date, date):
            acquisition_date = acquisition_date.strftime("%Y-%m-%d")

        # form data for flight creation
        data = {
            "name": name,
            "acquisition_date": acquisition_date,
            "altitude": altitude,
            "side_overlap": side_overlap,
            "forward_overlap": forward_overlap,
            "sensor": sensor,
            "platform": platform,
            "pilot_id": pilot_id,
        }

        # post form data
        response_data = self.client.make_post_request(endpoint, json=data)

        # return flight model
        flight = models.Flight(
            self.client, **schemas.Flight.from_dict(response_data).__dict__
        )
        return flight

    def get_flight(self, flight_id: str) -> Optional[models.Flight]:
        """Request single flight by ID. Flight must be active and viewable by user.

        Args:
            flight_id (str): Flight ID.

        Returns:
            Optional[models.Flight]: Flight matching ID or None.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights/{flight_id}"
        response_data = self.client.make_get_request(endpoint)

        flight = schemas.Flight.from_dict(response_data)
        return models.Flight(self.client, **flight.__dict__)

    def get_flights(self, has_raster: Optional[bool] = False) -> List[models.Flight]:
        """Return list of all active flights in project.

        Args:
            has_raster (Optional[bool], optional): Only return flights with active raster data products. Excludes non-raster data products. Defaults to False.

        Returns:
            List[models.Flight]: List of flights.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights"
        response_data = self.client.make_get_request(
            endpoint, params={"has_raster": has_raster}
        )

        flights = [
            models.Flight(self.client, **schemas.Flight.from_dict(flight).__dict__)
            for flight in response_data
        ]
        return FlightCollection(collection=flights)

    def get_project_boundary(self) -> Optional[GeoJSON]:
        """Return project boundary in GeoJSON format.

        Returns:
            GeoJSON: Project boundary in GeoJSON format.
        """
        if hasattr(self, "field"):
            return self.field

        endpoint = f"/api/v1/projects/{self.id}"
        response_data = self.client.make_get_request(endpoint)

        project = schemas.Project.from_dict(response_data)
        return project.field

    def update(self, **kwargs) -> None:
        """Update project attributes."""
        endpoint = f"/api/v1/projects/{self.id}"
        response_data = self.client.make_put_request(
            endpoint, json=json.loads(json.dumps(kwargs, default=str))
        )

        updated_project = schemas.Project.from_dict(response_data).__dict__
        for key, value in updated_project.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: Attribute '{key}' not found in Project class.")
        return None
