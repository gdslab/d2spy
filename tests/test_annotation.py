import os
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from requests import Session

from d2spy.api_client import APIClient
from d2spy.models.annotation import Annotation
from d2spy.models.annotation_collection import AnnotationCollection
from d2spy.models.data_product import DataProduct
from d2spy.schemas.annotation import Annotation as AnnotationSchema

from example_data import TEST_ANNOTATION, TEST_DATA_PRODUCT


class TestAnnotationSchema(TestCase):
    def test_from_dict(self):
        """Test Annotation schema deserialization"""
        annotation = AnnotationSchema.from_dict(TEST_ANNOTATION)

        self.assertEqual(annotation.id, TEST_ANNOTATION["id"])
        self.assertEqual(annotation.description, TEST_ANNOTATION["description"])
        self.assertEqual(annotation.geom, TEST_ANNOTATION["geom"])
        self.assertEqual(annotation.data_product_id, TEST_ANNOTATION["data_product_id"])
        self.assertEqual(annotation.visibility, TEST_ANNOTATION["visibility"])

    def test_from_dict_extracts_tags(self):
        """Test that tag names are extracted from tag_rows"""
        annotation = AnnotationSchema.from_dict(TEST_ANNOTATION)

        self.assertEqual(annotation.tags, ["boundary"])

    def test_from_dict_empty_tag_rows(self):
        """Test tag extraction with no tag_rows"""
        data = {**TEST_ANNOTATION, "tag_rows": []}
        annotation = AnnotationSchema.from_dict(data)

        self.assertEqual(annotation.tags, [])

    def test_from_dict_missing_tag_rows(self):
        """Test tag extraction when tag_rows key is absent"""
        data = {k: v for k, v in TEST_ANNOTATION.items() if k != "tag_rows"}
        annotation = AnnotationSchema.from_dict(data)

        self.assertEqual(annotation.tags, [])

    def test_from_dict_optional_fields(self):
        """Test that optional fields have sensible defaults"""
        minimal_data = {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "description": "Test",
            "geom": {"type": "Feature", "geometry": None, "properties": {}},
            "data_product_id": "2c2d5ce4-5611-4108-9f66-83ca51f5f52b",
        }
        annotation = AnnotationSchema.from_dict(minimal_data)

        self.assertIsNone(annotation.created_by_id)
        self.assertEqual(annotation.visibility, "owner")
        self.assertEqual(annotation.attachments, [])
        self.assertEqual(annotation.tags, [])
        self.assertIsNone(annotation.style)


class TestAnnotationModel(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(self.base_url, session)

        schema = AnnotationSchema.from_dict(TEST_ANNOTATION)
        self.annotation = Annotation(
            self.client,
            _project_id="24f77778-08d4-47d6-86a6-c6e32848370f",
            _flight_id="b4eb23cc-3d36-4586-b11c-a0a95b00d245",
            **schema.__dict__,
        )

    def test_init(self):
        """Test Annotation model initialization"""
        self.assertEqual(self.annotation.id, TEST_ANNOTATION["id"])
        self.assertEqual(self.annotation.description, TEST_ANNOTATION["description"])
        self.assertEqual(self.annotation.tags, ["boundary"])
        self.assertEqual(
            self.annotation._project_id,
            "24f77778-08d4-47d6-86a6-c6e32848370f",
        )

    def test_repr(self):
        """Test Annotation string representation"""
        repr_string = repr(self.annotation)

        self.assertIn("Annotation", repr_string)
        self.assertIn(TEST_ANNOTATION["id"], repr_string)
        self.assertIn(TEST_ANNOTATION["description"], repr_string)

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_update(self, mock_put):
        """Test updating annotation attributes"""
        updated_data = {
            **TEST_ANNOTATION,
            "description": "Updated description",
        }
        mock_put.return_value = updated_data

        self.annotation.update(description="Updated description")

        mock_put.assert_called_once_with(
            self.annotation._base_endpoint,
            json={"description": "Updated description"},
        )
        self.assertEqual(self.annotation.description, "Updated description")

    @patch("d2spy.api_client.APIClient.make_put_request")
    def test_update_tags(self, mock_put):
        """Test updating annotation tags"""
        updated_data = {
            **TEST_ANNOTATION,
            "tag_rows": [
                {
                    "id": "new-id",
                    "annotation_id": TEST_ANNOTATION["id"],
                    "tag_id": "new-tag-id",
                    "created_at": "",
                    "updated_at": "",
                    "tag": {"id": "new-tag-id", "name": "new-tag"},
                }
            ],
        }
        mock_put.return_value = updated_data

        self.annotation.update(tags=["new-tag"])

        self.assertEqual(self.annotation.tags, ["new-tag"])

    @patch("d2spy.api_client.APIClient.make_delete_request")
    def test_delete(self, mock_delete):
        """Test deleting an annotation"""
        mock_delete.return_value = TEST_ANNOTATION

        result = self.annotation.delete()

        mock_delete.assert_called_once_with(self.annotation._base_endpoint)
        self.assertTrue(result)

    def test_add_attachment_file_not_found(self):
        """Test add_attachment raises error for missing file"""
        with self.assertRaises(FileNotFoundError):
            self.annotation.add_attachment("/nonexistent/file.jpg")

    def test_add_attachment_unsupported_extension(self):
        """Test add_attachment raises error for unsupported file type"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                self.annotation.add_attachment(temp_path)
            self.assertIn("Unsupported file extension", str(ctx.exception))
        finally:
            os.remove(temp_path)

    def test_add_attachment_missing_context(self):
        """Test add_attachment raises error when project/flight context missing"""
        schema = AnnotationSchema.from_dict(TEST_ANNOTATION)
        annotation_no_context = Annotation(self.client, **schema.__dict__)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                annotation_no_context.add_attachment(temp_path)
            self.assertIn("Missing project/flight context", str(ctx.exception))
        finally:
            os.remove(temp_path)

    @patch("d2spy.models.annotation.tusc.TusClient")
    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_add_attachment_tus_upload(self, mock_get, mock_tus_client_cls):
        """Test add_attachment uploads via TUS with correct headers"""
        mock_get.return_value = {"id": "user-id"}

        # Set up TUS client mock
        mock_tus_client = MagicMock()
        mock_tus_client_cls.return_value = mock_tus_client
        mock_uploader = MagicMock()
        mock_uploader.get_file_size.return_value = 100
        mock_uploader.offset = 100  # Already done
        mock_tus_client.uploader.return_value = mock_uploader

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            temp_path = f.name

        try:
            self.annotation.add_attachment(temp_path)

            # Verify TUS client was created with correct endpoint
            mock_tus_client_cls.assert_called_once_with(f"{self.base_url}/files")

            # Verify headers include annotation-specific fields
            set_headers_call = mock_tus_client.set_headers.call_args[0][0]
            self.assertEqual(set_headers_call["X-Data-Type"], "annotation_attachment")
            self.assertEqual(
                set_headers_call["X-Annotation-ID"], str(self.annotation.id)
            )
            self.assertEqual(
                set_headers_call["X-Data-Product-ID"],
                str(self.annotation.data_product_id),
            )
            self.assertEqual(
                set_headers_call["X-Project-ID"],
                self.annotation._project_id,
            )
            self.assertEqual(
                set_headers_call["X-Flight-ID"],
                self.annotation._flight_id,
            )
        finally:
            os.remove(temp_path)

    @patch("d2spy.api_client.APIClient.make_delete_request")
    def test_delete_attachment(self, mock_delete):
        """Test deleting an attachment"""
        attachment_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        mock_delete.return_value = {}

        result = self.annotation.delete_attachment(attachment_id)

        expected_endpoint = (
            f"{self.annotation._base_endpoint}/attachments/{attachment_id}"
        )
        mock_delete.assert_called_once_with(expected_endpoint)
        self.assertTrue(result)

    def test_download_attachment(self):
        """Test downloading an attachment to local file"""
        attachment_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"

        # Mock session.get to return a streaming response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"file_content"]
        self.client.session.get = MagicMock(return_value=mock_response)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            out_path = f.name

        try:
            self.annotation.download_attachment(attachment_id, out_path)

            # Verify file was written
            with open(out_path, "rb") as f:
                self.assertEqual(f.read(), b"file_content")

            # Verify correct URL was called
            expected_url = (
                f"{self.base_url}{self.annotation._base_endpoint}"
                f"/attachments/{attachment_id}/download"
            )
            self.client.session.get.assert_called_once_with(
                expected_url, stream=True, timeout=60
            )
        finally:
            os.remove(out_path)


class TestAnnotationCollection(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(self.base_url, session)

        # Create annotations with different tags and visibilities
        annotation1_data = {**TEST_ANNOTATION, "tags": ["boundary", "field-1"]}
        annotation2_data = {
            **TEST_ANNOTATION,
            "id": "99999999-0000-1111-2222-333333333333",
            "tags": ["damage"],
            "visibility": "project",
        }

        self.annotation1 = Annotation(self.client, **annotation1_data)
        self.annotation2 = Annotation(self.client, **annotation2_data)
        self.collection = AnnotationCollection(
            collection=[self.annotation1, self.annotation2]
        )

    def test_len(self):
        """Test collection length"""
        self.assertEqual(len(self.collection), 2)

    def test_getitem(self):
        """Test collection indexing"""
        self.assertEqual(self.collection[0], self.annotation1)
        self.assertEqual(self.collection[1], self.annotation2)

    def test_repr(self):
        """Test collection repr"""
        repr_string = repr(self.collection)
        self.assertIn("AnnotationCollection", repr_string)

    def test_filter_by_tag(self):
        """Test filtering by tag"""
        filtered = self.collection.filter_by_tag("boundary")

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], self.annotation1)

    def test_filter_by_tag_case_insensitive(self):
        """Test filtering by tag is case insensitive"""
        filtered = self.collection.filter_by_tag("DAMAGE")

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], self.annotation2)

    def test_filter_by_tag_no_match(self):
        """Test filtering by tag with no matches"""
        filtered = self.collection.filter_by_tag("nonexistent")

        self.assertEqual(len(filtered), 0)

    def test_filter_by_visibility(self):
        """Test filtering by visibility"""
        filtered = self.collection.filter_by_visibility("project")

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], self.annotation2)

    def test_filter_by_visibility_owner(self):
        """Test filtering by owner visibility"""
        filtered = self.collection.filter_by_visibility("owner")

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], self.annotation1)


class TestDataProductAnnotations(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://example.com"
        session = Session()
        session.cookies.set("access_token", "fake_token")
        self.client = APIClient(self.base_url, session)
        self.data_product = DataProduct(self.client, **TEST_DATA_PRODUCT)
        self.annotations_endpoint = (
            f"/api/v1/projects/24f77778-08d4-47d6-86a6-c6e32848370f"
            f"/flights/{TEST_DATA_PRODUCT['flight_id']}"
            f"/data_products/{TEST_DATA_PRODUCT['id']}/annotations"
        )

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_add_annotation(self, mock_post):
        """Test adding an annotation to a data product"""
        mock_post.return_value = TEST_ANNOTATION

        geom = TEST_ANNOTATION["geom"]
        annotation = self.data_product.add_annotation(
            description="Field boundary annotation",
            geom=geom,
            tags=["boundary"],
            visibility="owner",
        )

        # Verify correct endpoint
        mock_post.assert_called_once_with(
            self.annotations_endpoint,
            json={
                "description": "Field boundary annotation",
                "geom": geom,
                "tags": ["boundary"],
                "visibility": "owner",
            },
        )

        # Verify returned annotation
        self.assertIsInstance(annotation, Annotation)
        self.assertEqual(annotation.description, "Field boundary annotation")
        self.assertEqual(annotation.tags, ["boundary"])

        # Verify context was injected
        self.assertEqual(
            annotation._project_id,
            "24f77778-08d4-47d6-86a6-c6e32848370f",
        )
        self.assertEqual(annotation._flight_id, str(TEST_DATA_PRODUCT["flight_id"]))

    @patch("d2spy.api_client.APIClient.make_post_request")
    def test_add_annotation_minimal(self, mock_post):
        """Test adding annotation with only required fields"""
        mock_post.return_value = TEST_ANNOTATION

        geom = TEST_ANNOTATION["geom"]
        self.data_product.add_annotation(
            description="Simple annotation",
            geom=geom,
        )

        # Verify tags and style are not included when not provided
        call_json = mock_post.call_args[1]["json"]
        self.assertNotIn("tags", call_json)
        self.assertNotIn("style", call_json)
        self.assertEqual(call_json["visibility"], "owner")

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_annotations(self, mock_get):
        """Test getting all annotations for a data product"""
        mock_get.return_value = [TEST_ANNOTATION, TEST_ANNOTATION]

        annotations = self.data_product.get_annotations()

        mock_get.assert_called_once_with(self.annotations_endpoint)

        self.assertIsInstance(annotations, AnnotationCollection)
        self.assertEqual(len(annotations), 2)
        self.assertIsInstance(annotations[0], Annotation)

    @patch("d2spy.api_client.APIClient.make_get_request")
    def test_get_annotation(self, mock_get):
        """Test getting a single annotation by ID"""
        mock_get.return_value = TEST_ANNOTATION

        annotation_id = TEST_ANNOTATION["id"]
        annotation = self.data_product.get_annotation(annotation_id)

        mock_get.assert_called_once_with(f"{self.annotations_endpoint}/{annotation_id}")

        self.assertIsInstance(annotation, Annotation)
        self.assertEqual(annotation.id, annotation_id)
