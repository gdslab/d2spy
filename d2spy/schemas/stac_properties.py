from typing import List, Union, TypedDict


class Stats(TypedDict):
    minimum: float
    maximum: float
    mean: float
    stddev: float


class _STACRasterProperties(TypedDict):
    data_type: str
    stats: Stats


class STACRasterProperties(_STACRasterProperties, total=False):
    nodata: Union[int, float]
    unit: str


class STACEOProperties(TypedDict):
    name: str
    description: str


class STACProperties(TypedDict):
    raster: List[STACRasterProperties]
    eo: List[STACEOProperties]
