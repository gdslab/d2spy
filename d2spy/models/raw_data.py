from d2spy.api_client import APIClient


class RawData:
    def __init__(self, client: APIClient, **kwargs):
        self.client = client
        # raw data attributes returned from API
        self.__dict__.update(kwargs)

    def __repr__(self):
        return (
            f"RawData(data_type={self.data_type!r}, "
            f"filepath={self.filepath!r}, "
            f"original_filename={self.original_filename!r}, status={self.status!r}, "
            f"is_active={self.is_active!r}, url={self.url!r})"
        )
