from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class Annotation:
    id: UUID
    description: str
    geom: Dict[str, Any]
    data_product_id: UUID
    created_by_id: Optional[UUID]
    visibility: str
    created_at: str
    updated_at: str
    attachments: List[Dict[str, Any]]
    tags: List[str]
    style: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Annotation":
        # Extract tag names from tag_rows[].tag.name
        tags: List[str] = []
        for tag_row in data.get("tag_rows", []):
            tag_obj = tag_row.get("tag")
            if tag_obj and tag_obj.get("name"):
                tags.append(tag_obj["name"])

        return cls(
            id=data["id"],
            description=data["description"],
            geom=data["geom"],
            data_product_id=data["data_product_id"],
            created_by_id=data.get("created_by_id"),
            visibility=data.get("visibility", "owner"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            attachments=data.get("attachments", []),
            tags=tags,
            style=data.get("style"),
        )
