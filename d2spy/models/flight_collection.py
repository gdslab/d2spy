from datetime import date, datetime
from difflib import SequenceMatcher
from typing import List, Union

from d2spy.models.flight import Flight


class FlightCollection:
    """Collection of Data to Science flights associated with a project."""

    def __init__(self, collection: List[Flight] = []):
        self.collection = collection

    def __getitem__(self, index: int) -> Flight:
        return self.collection[int(index)]

    def __len__(self) -> int:
        return len(self.collection)

    def __repr__(self) -> str:
        return f"FlightCollection({self.collection})"

    def filter_by_date(self, start_date: date, end_date: date) -> "FlightCollection":
        """Returns collection of flights within the acquisition date range.

        Args:
            start_date (date): Starting date for the flight acquisition date range.
            end_date (date): Ending date for the flight acquisition date range.

        Returns:
            FlightCollection: Collection of flights within the acquisition date range.
        """
        filtered_collection = [
            flight
            for flight in self.collection
            if convert_from_str_to_date(flight.acquisition_date) >= start_date
            and convert_from_str_to_date(flight.acquisition_date) <= end_date
        ]
        return FlightCollection(collection=filtered_collection)

    def filter_by_sensor(self, sensor: str, exact: bool = False) -> "FlightCollection":
        """Returns collection of flights with specified sensor.

        Args:
            sensor (str): Sensor of interest.
            exact (bool, optional): Must be exact match. Defaults to False.

        Returns:
            FlightCollection: Collection of flights with matching sensor.
        """
        filtered_collection = [
            flight
            for flight in self.collection
            if is_match(sensor, flight.sensor, exact)
        ]
        return FlightCollection(collection=filtered_collection)


def convert_from_str_to_date(date_str: Union[date, str]) -> date:
    """Convert date string to date object.

    Args:
        date_str (str): Date represented by string object.

    Returns:
        date: Converted date.
    """
    try:
        if isinstance(date_str, date):
            # already date object, return it
            return date_str
        if isinstance(date_str, str):
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        raise
    except Exception as error:
        print(
            f"Unable to convert acquistion date {date_str} to date object. "
            "Acquisition date string must be in %Y-%m-%d format."
        )
        raise (error)


def is_match(a: str, b: str, exact: bool = False) -> bool:
    """Case insensitive method that checks if "a" and "b" match or
    match to within a degree of similarity (0.8).

    Args:
        a (str): User supplied string.
        b (str): Internal string.
        exact (bool, optional): True if must be exact match. Defaults to False.

    Returns:
       bool: True if "a" and "b" match.
    """
    if exact:
        return a.lower() == b.lower()
    else:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.8
