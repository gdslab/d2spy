from typing import Any, Dict, List, Literal, TypedDict
from uuid import UUID


class PolygonGeometry(TypedDict):
    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]


class ProjectProperties(TypedDict):
    id: UUID
    center_x: float
    center_y: float


class ProjectBoundaryGeoJSON(TypedDict):
    type: str
    geometry: PolygonGeometry
    properties: ProjectProperties


class Feature(TypedDict):
    type: Literal["Feature"]
    geometry: PolygonGeometry
    properties: Dict[Any, Any]


class FeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: List[Feature]


class MapLayerFeatureCollection(FeatureCollection):
    metadata: Dict[str, Any]
