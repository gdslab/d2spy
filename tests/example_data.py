from datetime import date, datetime, timedelta

# Example data product response from API
TEST_DATA_PRODUCT = {
    "data_type": "dsm",
    "filepath": "/some/filepath/dsm.tif",
    "original_filename": "dsm.tif",
    "stac_properties": {
        "raster": [
            {
                "data_type": "float32",
                "stats": {
                    "minimum": 187.849,
                    "maximum": 188.088,
                    "mean": 187.959,
                    "stddev": 0.038,
                },
                "nodata": None,
            }
        ],
        "eo": [{"name": "b1", "description": "Gray"}],
    },
    "is_active": True,
    "is_initial_processing_completed": True,
    "id": "2c2d5ce4-5611-4108-9f66-83ca51f5f52b",
    "flight_id": "b4eb23cc-3d36-4586-b11c-a0a95b00d245",
    "user_style": {
        "max": 188.088,
        "min": 187.849,
        "mode": "minMax",
        "userMax": 188.088,
        "userMin": 187.849,
        "colorRamp": "rainbow",
        "meanStdDev": 2,
    },
    "deactivated_at": None,
    "public": False,
    "status": "SUCCESS",
    "url": "https://example.com/some/filepath/dsm.tif",
}


# Example flight response from API
TEST_FLIGHT = {
    "acquisition_date": str(date.today()),
    "altitude": 40,
    "side_overlap": 85,
    "forward_overlap": 85,
    "sensor": "RGB",
    "platform": "M350",
    "name": "Test Flight",
    "is_active": True,
    "pilot_id": "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5",
    "id": "b4eb23cc-3d36-4586-b11c-a0a95b00d245",
    "deactivated_at": None,
    "read_only": False,
    "project_id": "24f77778-08d4-47d6-86a6-c6e32848370f",
    "data_products": [],
}

# Example project response from API
TEST_PROJECT = {
    "id": "24f77778-08d4-47d6-86a6-c6e32848370f",
    "title": "Test Project",
    "description": "Project for testing d2spy package.",
    "deactivated_at": False,
    "field": {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [30.0, 10.0],
                    [40.0, 10.0],
                    [40.0, 20.0],
                    [30.0, 20.0],
                    [30.0, 10.0],
                ]
            ],
        },
    },
    "flight_count": 0,
    "harvest_date": datetime.now(),
    "is_active": True,
    "location_id": "3a3cd25-450a-48e5-86a8-55bb3fa54838",
    "planting_date": datetime.now() - timedelta(days=90),
    "role": "manager",
    "team_id": None,
}

# Example project from mutli projects response from API
TEST_MULTI_PROJECT = {
    "id": "24f77778-08d4-47d6-86a6-c6e32848370f",
    "title": "Test Project",
    "description": "Project for testing d2spy package.",
    "centroid": {"x": 40, "y": 20},
    "role": "manager",
    "flight_count": 0,
}

# Example list of feature collections response from API
TEST_FEATURE_COLLECTION = [
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.944240742, 41.444203148],
                            [-86.944180887, 41.444203119],
                            [-86.944180925, 41.444158081],
                            [-86.944240781, 41.44415811],
                            [-86.944240742, 41.444203148],
                        ]
                    ],
                },
                "properties": {
                    "id": "01c171e7-6042-42f6-b2c5-be644fd86561",
                    "layer_name": "Polygon_Data.zip",
                    "layer_id": "IaU7XchVIZA",
                    "properties": {"col": 1, "row": 1},
                    "is_active": True,
                    "project_id": "24f77778-08d4-47d6-86a6-c6e32848370f",
                    "flight_id": None,
                    "data_product_id": None,
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.944689716, 41.444135808],
                            [-86.944629861, 41.444135779],
                            [-86.944629899, 41.444090742],
                            [-86.944689755, 41.44409077],
                            [-86.944689716, 41.444135808],
                        ]
                    ],
                },
                "properties": {
                    "id": "02c953c0-7b4e-4c13-b058-c201e07ce6e5",
                    "layer_name": "Polygon_Data.zip",
                    "layer_id": "IaU7XchVIZA",
                    "properties": {"col": 2, "row": 1},
                    "is_active": True,
                    "project_id": "24f77778-08d4-47d6-86a6-c6e32848370f",
                    "flight_id": None,
                    "data_product_id": None,
                },
            },
        ],
        "metadata": {
            "preview_url": (
                "http://example.com/static/projects/24f77778-08d4-47d6-"
                "86a6-c6e32848370f/vector/IaU7XchVIZA/preview.png"
            )
        },
    },
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.943995035, 41.443944262],
                            [-86.943971093, 41.44394425],
                            [-86.943971108, 41.443926235],
                            [-86.94399505, 41.443926247],
                            [-86.943995035, 41.443944262],
                        ]
                    ],
                },
                "properties": {
                    "id": "05abd543-f29c-4158-b1e6-d8de370b69fb",
                    "layer_name": "sample_sites_wgs84.geojson",
                    "layer_id": "E5KGg2CEUUw",
                    "properties": {"col": 12, "row": 4},
                    "is_active": True,
                    "project_id": "24f77778-08d4-47d6-86a6-c6e32848370f",
                    "flight_id": None,
                    "data_product_id": None,
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.944174555, 41.443998395],
                            [-86.944150612, 41.443998383],
                            [-86.944150628, 41.443980368],
                            [-86.94417457, 41.44398038],
                            [-86.944174555, 41.443998395],
                        ]
                    ],
                },
                "properties": {
                    "id": "09fa3bdb-f76f-420b-9c0d-d7060618d0eb",
                    "layer_name": "sample_sites_wgs84.geojson",
                    "layer_id": "E5KGg2CEUUw",
                    "properties": {"col": 7, "row": 2},
                    "is_active": True,
                    "project_id": "24f77778-08d4-47d6-86a6-c6e32848370f",
                    "flight_id": None,
                    "data_product_id": None,
                },
            },
        ],
        "metadata": {
            "preview_url": (
                "http://example.com/static/projects/24f77778-08d4-"
                "47d6-86a6-c6e32848370f/vector/E5KGg2CEUUw/preview.png"
            )
        },
    },
]

TEST_USER = {
    "email": "d2suser@example.com",
    "first_name": "string",
    "last_name": "string",
    "is_email_confirmed": True,
    "is_approved": True,
    "id": "dd18a0ea-d6fe-49e2-b16b-cb0faa7548b5",
    "created_at": "2024-08-29T13:49:55.191Z",
    "api_access_token": "abc123",
    "exts": [],
    "is_superuser": False,
    "profile_url": "https://example.com",
}
