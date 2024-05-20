from typing import NotRequired, TypedDict


class Stats(TypedDict):
    minimum: float
    maximum: float
    mean: float
    stddev: float


class STACRasterProperties(TypedDict):
    data_type: str
    stats: Stats
    nodata: NotRequired[int | float | None]
    unit: NotRequired[str | None]


class STACEOProperties(TypedDict):
    name: str
    description: str


class STACProperties(TypedDict):
    raster: list[STACRasterProperties]
    eo: list[STACEOProperties]
