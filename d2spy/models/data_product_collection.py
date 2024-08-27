from typing import List

from d2spy.models.data_product import DataProduct


class DataProductCollection:
    """Collection of Data to Science data products associated with a flight."""

    def __init__(self, collection: List[DataProduct] = []):
        self.collection = collection

    def __getitem__(self, index: int) -> DataProduct:
        return self.collection[int(index)]

    def __len__(self) -> int:
        return len(self.collection)

    def __repr__(self) -> str:
        return f"DataProductCollection({self.collection})"

    def filter_by_data_type(self, data_type: str) -> "DataProductCollection":
        """Returns list of data products matching data type.

        Args:
            data_type (str): Data type to filter by.

        Returns:
            DataProductCollection: Collection of data products matching data type.
        """
        filtered_collection = [
            data_product
            for data_product in self.collection
            if data_product.data_type.lower() == data_type.lower()
        ]
        return DataProductCollection(collection=filtered_collection)
