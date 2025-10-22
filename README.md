# Welcome to Data to Science Python (d2spy)

[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gdslab/d2spy/blob/master)
[![Jupyter Notebook](https://img.shields.io/badge/Open%20in%20JuypterHub%20-%20%233776AB?logo=jupyter&logoColor=%23F37626&labelColor=%23F5F5F5)](https://lab.d2s.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <img
    src="https://py.d2s.org/assets/d2s-logo.png"
    alt="Data to Science logo"
    width="128"
  >
</p>

D2spy is a Python package for interacting with Data to Science instances.

## Installation

Install the core package with minimal dependencies:

```bash
pip install d2spy
```

Or install with geospatial features for raster clipping and EXIF extraction:

```bash
pip install d2spy[geo]
```

### What's the difference?

**Core installation (`d2spy`):**
- Requires only `requests` library
- Full API access: authentication, projects, flights, data uploads
- Server-side analysis: NDVI, ExG, zonal statistics (job submission)
- Perfect for: lightweight integrations, CI/CD pipelines, QGIS plugins (which already include geo libraries)

**Geo installation (`d2spy[geo]`):**
- Adds `rasterio`, `geopandas`, and `exifread` libraries
- Client-side geospatial processing: raster clipping, EXIF data extraction, bounding box generation
- Required for: `DataProduct.clip()`, `get_exif_data()`, `get_bounding_box_from_exif_data()`

### Bundling with QGIS Plugins

If you're bundling d2spy in a QGIS plugin, extract the wheel and copy the `d2spy` folder into your plugin directory. Since QGIS already includes most geospatial libraries, geo features will work automatically without needing to install `d2spy[geo]`.

## Features

### Core Features (available with base installation)
- Sign in to your Data to Science instance
- Access your projects, flights, and data products
- Create new projects and flights
- Upload data products to flights (rasters, point clouds, raw data)
- Server-side analysis: NDVI, ExG, zonal statistics

### Geospatial Features (requires `d2spy[geo]`)
- Client-side raster clipping by polygon
- Extract EXIF data from images
- Generate bounding boxes from image collections

## Documentation

- [Homepage](https://py.d2s.org/)
- [Guides](https://py.d2s.org/guides)
- [API Reference](https://py.d2s.org/api_client/)
