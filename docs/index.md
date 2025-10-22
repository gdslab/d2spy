# Welcome to Data to Science Python (d2spy)

[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gdslab/d2spy/blob/master)
[![Jupyter Notebook](https://img.shields.io/badge/Open%20in%20JuypterHub%20-%20%233776AB?logo=jupyter&logoColor=%23F37626&labelColor=%23F5F5F5)](https://lab.d2s.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img
    src="./assets/d2s-logo-blue.png"
    alt="Data to Science logo"
    width="256"
>

</p>

D2spy is a Python package for interacting with Data to Science instances.

## Features

- Sign in to your Data to Science instance
- Access your projects, flights, and data products
- Create new projects and flights
- Upload data products to flights

## Installation

D2spy supports two installation modes:

**Core Installation** (minimal dependencies):
```bash
pip install d2spy
```
Includes full API access for authentication, project/flight management, data uploads, and server-side analysis tools (NDVI, ExG, zonal statistics).

**Geo Installation** (with geospatial dependencies):
```bash
pip install d2spy[geo]
```
Adds client-side geospatial processing capabilities including raster clipping, EXIF extraction, and bounding box generation. Requires `rasterio`, `geopandas`, and `exifread`.

## Learn more

👉 **Visit the [official D2S homepage](https://d2s.org) to learn more.**
