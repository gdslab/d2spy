from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.data_product import DataProduct
from d2spy.models.data_product_collection import DataProductCollection

from example_data import TEST_DATA_PRODUCT


class TestDataProductCollection(TestCase):
    def test_filter_by_data_type(self):
        # Setup a test session
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")

        # Instantiate the APIClient with a test URL and the test session
        client = APIClient(base_url, session)

        # Test data product collection
        collection = DataProductCollection(
            collection=[
                DataProduct(client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(client, **{**TEST_DATA_PRODUCT, "data_type": "ortho"}),
                DataProduct(client, **{**TEST_DATA_PRODUCT, "data_type": "ortho"}),
            ]
        )

        # Find data products with "dsm" data type
        filtered_collection = collection.filter_by_data_type("dsm")

        # filter_by_data_type should return new DataProductCollecton with results
        self.assertIsInstance(filtered_collection, DataProductCollection)
        # Three data products have the "dsm" data type
        self.assertEqual(len(filtered_collection), 3)
        # Each item in returned DataProductCollection should be DataProduct
        for data_product in filtered_collection:
            self.assertIsInstance(data_product, DataProduct)
