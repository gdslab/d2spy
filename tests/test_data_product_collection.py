from unittest import TestCase

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.data_product import DataProduct
from d2spy.models.data_product_collection import DataProductCollection

from example_data import TEST_DATA_PRODUCT


class TestDataProductCollection(TestCase):
    def setUp(self):
        base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(base_url, session)

    def test_filter_by_data_type(self):
        collection = DataProductCollection(
            collection=[
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "ortho"}),
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "ortho"}),
            ]
        )

        # Find data products with "dsm" data type
        filtered_collection = collection.filter_by_data_type("dsm")

        # filter_by_data_type should return new DataProductCollection with results
        self.assertIsInstance(filtered_collection, DataProductCollection)
        # Three data products have the "dsm" data type
        self.assertEqual(len(filtered_collection), 3)
        # Each item in returned DataProductCollection should be DataProduct
        for data_product in filtered_collection:
            self.assertIsInstance(data_product, DataProduct)

    def test_filter_by_data_type_no_match(self):
        collection = DataProductCollection(
            collection=[
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
            ]
        )

        filtered = collection.filter_by_data_type("point_cloud")
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, DataProductCollection)

    def test_filter_by_data_type_case_insensitive(self):
        collection = DataProductCollection(
            collection=[
                DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"}),
            ]
        )

        filtered = collection.filter_by_data_type("DSM")
        self.assertEqual(len(filtered), 1)

    def test_empty_collection(self):
        collection = DataProductCollection()

        self.assertEqual(len(collection), 0)

        filtered = collection.filter_by_data_type("dsm")
        self.assertEqual(len(filtered), 0)
        self.assertIsInstance(filtered, DataProductCollection)

    def test_getitem(self):
        dp1 = DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "dsm"})
        dp2 = DataProduct(self.client, **{**TEST_DATA_PRODUCT, "data_type": "ortho"})
        collection = DataProductCollection(collection=[dp1, dp2])

        self.assertEqual(collection[0].data_type, "dsm")
        self.assertEqual(collection[1].data_type, "ortho")
