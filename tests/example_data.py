from datetime import date, datetime, timedelta

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
