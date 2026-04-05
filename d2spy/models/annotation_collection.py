from typing import List

from d2spy.models.annotation import Annotation


class AnnotationCollection:
    """Collection of annotations associated with a data product."""

    def __init__(self, collection: List[Annotation] = []):
        self.collection = collection

    def __getitem__(self, index: int) -> Annotation:
        return self.collection[int(index)]

    def __len__(self) -> int:
        return len(self.collection)

    def __repr__(self) -> str:
        return f"AnnotationCollection({self.collection})"

    def filter_by_tag(self, tag: str) -> "AnnotationCollection":
        """Returns annotations that have the specified tag.

        Args:
            tag (str): Tag name to filter by (case-insensitive).

        Returns:
            AnnotationCollection: Filtered collection.
        """
        filtered = [
            annotation
            for annotation in self.collection
            if tag.lower() in [t.lower() for t in annotation.tags]
        ]
        return AnnotationCollection(collection=filtered)

    def filter_by_visibility(self, visibility: str) -> "AnnotationCollection":
        """Returns annotations matching the specified visibility.

        Args:
            visibility (str): Visibility to filter by ("owner" or "project").

        Returns:
            AnnotationCollection: Filtered collection.
        """
        filtered = [
            annotation
            for annotation in self.collection
            if annotation.visibility.lower() == visibility.lower()
        ]
        return AnnotationCollection(collection=filtered)
