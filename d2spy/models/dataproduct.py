from datetime import date, datetime
from dataclasses import dataclass
from typing import List, Union
from uuid import UUID


@dataclass
class DataProduct:
    id: UUID
    data_type: str
    filepath: str
    original_filename: str
    is_active: bool
    flight_id: UUID
    deactivated_at: Union[datetime, None]
    public: bool
    status: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "DataProduct":
        return cls(
            id=data["id"],
            data_type=data["data_type"],
            filepath=data["filepath"],
            original_filename=data["original_filename"],
            is_active=data["is_active"],
            flight_id=data["flight_id"],
            deactivated_at=data["deactivated_at"],
            public=data["public"],
            status=data["status"],
            url=data["url"],
        )
