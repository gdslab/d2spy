from datetime import date, datetime
from typing import List

from d2spy.models.flight import Flight


class FlightCollection:
    """Collection of Data to Science flights associated with a project."""

    def __init__(self, collection: List[Flight] = []) -> None:
        self.collection = collection

    def __getitem__(self, index: int) -> Flight:
        return self.collection[int(index)]

    def __len__(self) -> int:
        return len(self.collection)

    def __repr__(self) -> str:
        return f"FlightCollection({self.collection})"

    def filter_by_date(self, start_date: date, end_date: date) -> List[Flight]:
        """Returns list of flights with at least one flight within the date range.

        Args:
            start_date (date): Starting date for the flight acquisition date range.
            end_date (date): Ending date for the flight acquisition date range.

        Returns:
            List[Flight]: List of flights with a flight within the date range.
        """
        filtered_collection = [
            flight
            for flight in self.collection
            if convert_from_str_to_date(flight.acquisition_date) >= start_date
            and convert_from_str_to_date(flight.acquisition_date) <= end_date
        ]
        return FlightCollection(collection=filtered_collection)


def convert_from_str_to_date(date_str: str) -> date:
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
    except Exception:
        print(
            f"Unable to convert acquistion date {date_str} to date object. Acquisition date string must be in %Y-%m-%d format."
        )
