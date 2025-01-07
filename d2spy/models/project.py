import json
from datetime import date, datetime
from typing import Any, cast, Dict, List, Literal, Optional, Union
from uuid import UUID

from d2spy import models, schemas
from d2spy.api_client import APIClient
from d2spy.extras.utils import ensure_dict, ensure_list_of_dict
from d2spy.models.flight_collection import FlightCollection
from d2spy.schemas.geojson import MapLayerFeatureCollection, ProjectBoundaryGeoJSON


class Project:
    id: UUID
    deactivated_at: Optional[datetime]
    description: str
    field: ProjectBoundaryGeoJSON
    flight_count: int
    harvest_date: Optional[date]
    is_active: bool
    location_id: UUID
    planting_date: Optional[date]
    role: Literal["owner", "manager", "viewer"]
    team_id: Optional[UUID]
    title: str

    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # project attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        repr_str = f"Project(title={self.title!r}, description={self.description!r}"

        if hasattr(self, "start_date") and self.start_date:
            repr_str += f", start_date={self.start_date!r}"

        if hasattr(self, "end_date") and self.end_date:
            repr_str += f", end_date={self.end_date!r}"

        repr_str += ")"

        return repr_str

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
            sensor (Literal["RGB", "Multispectral", "LiDAR", "Other"]): Camera sensor.
            platform (Union[Literal["Phantom_4", "M300", "M350"], str]): UAS platform.
            pilot_id (Optional[UUID]): ID of the flight's pilot. Defaults to None.

        Returns:
            models.Flight: Newly created flight.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights"

        # if pilot id not provided, use current user's id
        if not pilot_id:
            user = self.client.make_get_request("/api/v1/users/current")
            user = ensure_dict(user)
            pilot_id = user["id"]

        # form data for flight creation
        data = {
            "name": name,
            "acquisition_date": acquisition_date.strftime("%Y-%m-%d"),
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

    def add_map_layer(
        self, layer_name: str, feature_collection: Dict[str, Any]
    ) -> MapLayerFeatureCollection:
        """Add vector map layer to a project.

        Args:
            layer_name (str): Name of map layer.
            feature_collection (Dict[str, Any]): GeoJSON Feature Collection.

        Returns:
            MapLayerFeatureCollection: GeoJSON Feature Collection with D2S metadata.
        """
        endpoint = f"/api/v1/projects/{self.id}/vector_layers"

        # vector layer data
        data = {"layer_name": layer_name, "geojson": feature_collection}

        # post vector layer data
        response_data = self.client.make_post_request(endpoint, json=data)

        # return feature collection of vector layer
        return cast(MapLayerFeatureCollection, response_data)

    def get_flight(self, flight_id: str) -> Optional[models.Flight]:
        """Request single flight by ID. Flight must be active and viewable by user.

        Args:
            flight_id (str): Flight ID.

        Returns:
            Optional[models.Flight]: Flight matching ID or None.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights/{flight_id}"
        response_data = self.client.make_get_request(endpoint)
        response_data = ensure_dict(response_data)
        flight = schemas.Flight.from_dict(response_data)
        return models.Flight(self.client, **flight.__dict__)

    def get_flights(self, has_raster: Optional[bool] = False) -> FlightCollection:
        """Return list of all active flights in project.

        Args:
            has_raster (Optional[bool], optional): Only return flights with rasters.

        Returns:
            FlightCollection: Collection of flights.
        """
        endpoint = f"/api/v1/projects/{self.id}/flights"
        response_data = self.client.make_get_request(
            endpoint, params={"has_raster": has_raster}
        )
        response_data = ensure_list_of_dict(response_data)
        flights = [
            models.Flight(self.client, **schemas.Flight.from_dict(flight).__dict__)
            for flight in response_data
        ]
        return FlightCollection(collection=flights)

    def get_project_boundary(self) -> Optional[ProjectBoundaryGeoJSON]:
        """Return project boundary in GeoJSON format.

        Returns:
            ProjectBoundaryGeoJSON: Project boundary in GeoJSON format.
        """
        if hasattr(self, "field"):
            return self.field

        endpoint = f"/api/v1/projects/{self.id}"
        response_data = self.client.make_get_request(endpoint)
        response_data = ensure_dict(response_data)
        project = schemas.Project.from_dict(response_data)
        return project.field

    def get_map_layers(self) -> List[Dict[Any, Any]]:
        """Return list of GeoJSON FeatureCollections for all map layers
        associated with this project.

        Returns:
            List[Dict[Any, Any]]: List of GeoJSON FeatureCollections.
        """
        endpoint = f"/api/v1/projects/{self.id}/vector_layers"
        response_data = self.client.make_get_request(
            endpoint, params={"format": "json"}
        )
        response_data = ensure_list_of_dict(response_data)
        return response_data

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
