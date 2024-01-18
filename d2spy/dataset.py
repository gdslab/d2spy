from requests import Session
from typing import Sequence
from uuid import UUID

from .auth import Auth
from .extras.utils import pretty_print_response
from .models.dataproduct import DataProduct
from .models.flight import Flight
from .models.project import Project


class Dataset:
    """Retrieves projects, flights, and datasets for D2S user."""

    def __init__(self, auth: Auth) -> None:
        if not auth.session:
            print("no user logged in")

        self.host: str = auth.host
        self.session: Session = auth.session

    def get_projects(self) -> Sequence[Project]:
        """Fetches user's projects."""
        url = f"{self.host}/api/v1/projects"

        response = self.session.get(url)

        if response.status_code == 200:
            projects = response.json()
            return [Project.from_dict(project) for project in projects]
        else:
            pretty_print_response(response)
            return []

    def get_flights(self, project_id: UUID) -> Sequence[Flight]:
        """Fetches user's flights for specific project."""
        url = f"{self.host}/api/v1/projects/{project_id}/flights"

        response = self.session.get(url)

        if response.status_code == 200:
            flights = response.json()
            return [Flight.from_dict(flight) for flight in flights]
        else:
            pretty_print_response(response)
            return []

    def get_data_products(
        self, project_id: UUID, flight_id: UUID
    ) -> Sequence[DataProduct]:
        """Fetches user's data products for specific flight."""
        url = f"{self.host}/api/v1/projects/{project_id}/flights/{flight_id}"

        response = self.session.get(url)

        if response.status_code == 200:
            data = response.json()
            if "data_products" in data:
                data_products = data.get("data_products")
                return [
                    DataProduct.from_dict(data_product)
                    for data_product in data_products
                ]
            else:
                return []
        else:
            pretty_print_response(response)
            return []
