from datetime import date
from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.flight import Flight
from d2spy.models.flight_collection import FlightCollection

from example_data import TEST_FLIGHT


class TestFlightCollection(TestCase):
    def setUp(self):
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(base_url, session)

    def test_filter_by_date(self):
        collection = FlightCollection(
            collection=[
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 4, 30)},
                ),
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 1)},
                ),
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 15)},
                ),
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 31)},
                ),
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 6, 1)},
                ),
            ]
        )

        # Find flights with acquisition date during May 2024
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

    def test_filter_by_sensor(self):
        collection = FlightCollection(
            collection=[
                Flight(self.client, **{**TEST_FLIGHT, "sensor": "RGB"}),
                Flight(self.client, **{**TEST_FLIGHT, "sensor": "RGB"}),
                Flight(self.client, **{**TEST_FLIGHT, "sensor": "Multispectral"}),
                Flight(self.client, **{**TEST_FLIGHT, "sensor": "LiDAR"}),
                Flight(self.client, **{**TEST_FLIGHT, "sensor": "Other"}),
            ]
        )

        # Find flights with sensor "RGB"
        filtered_collection = collection.filter_by_sensor("RGB")

        # filter_by_sensor should return new FlightCollection with results
        self.assertIsInstance(filtered_collection, FlightCollection)
        # Two flights with "RGB" sensor
        self.assertEqual(len(filtered_collection), 2)
        # Each item in returned FlightCollection should be Flight
        for flight in filtered_collection:
            self.assertIsInstance(flight, Flight)

        # Find flights with sensor "MultiSpectrel" (typo) exact match required
        filtered_collection2 = collection.filter_by_sensor("MultiSpectrel", exact=True)

        # Since this is an exact match, nothing should be returned due to the typo
        self.assertEqual(len(filtered_collection2), 0)

        # Find flights with sensor "MultiSpectrel" (typo) no exact match required
        filtered_collection3 = collection.filter_by_sensor("MultiSpectrel")

        # Should find match even with typo
        self.assertEqual(len(filtered_collection3), 1)

    def test_filter_by_date_no_match(self):
        collection = FlightCollection(
            collection=[
                Flight(
                    self.client,
                    **{**TEST_FLIGHT, "acquisition_date": date(2024, 5, 1)},
                ),
            ]
        )

        filtered = collection.filter_by_date(
            start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)
        )
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, FlightCollection)

    def test_empty_collection(self):
        collection = FlightCollection()

        self.assertEqual(len(collection), 0)

        filtered = collection.filter_by_date(
            start_date=date(2024, 1, 1), end_date=date(2024, 12, 31)
        )
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, FlightCollection)
