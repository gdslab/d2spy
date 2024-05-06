from d2spy.api_client import APIClient


class DataProduct:
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # data product attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"DataProduct(id={self.id!r}, data_type={self.data_type!r}, "
            f"filepath={self.filepath!r}, original_filename={self.original_filename!r}, "
            f"is_active={self.is_active!r}, flight_id={self.flight_id!r}, "
            f"public={self.public!r}, status={self.status!r}, url={self.url!r})"
        )
