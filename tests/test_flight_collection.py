from datetime import date
from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.flight import Flight
from d2spy.models.flight_collection import FlightCollection

from example_data import TEST_FLIGHT


class TestFlightCollection(TestCase):
    def test_filter_by_date(self):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test flight collection
        collection = FlightCollection(
            collection=[
                Flight(
                    client, **{**TEST_FLIGHT, "acquisition_date": date(2024, 4, 30)}
                ),
                Flight(client, **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 1)}),
                Flight(
                    client, **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 15)}
                ),
                Flight(
                    client, **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 31)}
                ),
                Flight(client, **{**TEST_FLIGHT, "acquisition_date": date(2024, 6, 1)}),
            ]
        )

        # Find flights with acquistion date during May 2024
        filtered_collection = collection.filter_by_date(
            start_date=date(2024, 5, 1), end_date=date(2024, 5, 31)
        )

        # filter_by_date should return new FlightCollection with results
        self.assertIsInstance(filtered_collection, FlightCollection)
        # Three flight acquisition dates are in May 2024
        self.assertEqual(len(filtered_collection), 3)
        # Each item in returned FlightCollection should be Flight
        for flight in filtered_collection:
            self.assertIsInstance(flight, Flight)
