from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Optional
from uuid import UUID


@dataclass
class Job:
    id: UUID
    name: str
    state: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    data_product_id: Optional[UUID]
    raw_data_id: Optional[UUID]
    check_status: Callable[[], str]

    @classmethod
    def from_dict(cls, data: dict, check_status_fn: Callable[[], str]) -> "Job":
        return cls(
            id=data["id"],
            name=data["name"],
            state=data["state"],
            status=data["status"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            data_product_id=data["data_product_id"],
            raw_data_id=data["raw_data_id"],
            check_status=check_status_fn,
        )
