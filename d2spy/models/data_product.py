from datetime import datetime
from typing import Optional
from uuid import UUID

from d2spy.api_client import APIClient
from d2spy.schemas.stac_properties import STACProperties


class DataProduct:
    id: UUID
    data_type: str
    filepath: str
    original_filename: str
    is_active: bool
    flight_id: UUID
    deactivated_at: Optional[datetime]
    public: bool
    stac_properties: STACProperties
    status: str
    url: str

    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # data product attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"DataProduct(data_type={self.data_type!r}, "
            f"filepath={self.filepath!r}, "
            f"original_filename={self.original_filename!r}, "
            f"is_active={self.is_active!r}, public={self.public!r}, "
            f"stac_properties={self.stac_properties!r}, status={self.status!r}, "
            f"url={self.url!r})"
        )
