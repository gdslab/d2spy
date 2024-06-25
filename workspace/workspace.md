## Usage

To use this class, first import it into your Python script:

```python
from d2spy.workspace import Workspace
```

Then create an instance of `Workspace`:

```python
workspace = Workspace(base_url, session)
```

## Example #1 - Accessing data

```python
from d2spy.auth import Auth
from d2spy.workspace import Workspace

# Base URL for D2S instance
base_url = "http://localhost:8000"

# Create an instance of Auth
auth = Auth(base_url)

# Enter your password when prompted
auth.login(email="your_d2s_email@example.com")

# Get active session from auth
session = auth.session

# Create Workspace instance for session
workspace = Workspace(base_url, session)

# Fetch Projects accesible by user
projects = workspace.get_projects()
for project in projects:
    print(project.title)

# Fetch flights for project
flights = projects[0].get_flights()
for flight in flights:
    print(flight.acquisition_date)

# Fetch data products for flight
data_products = flights[0].get_data_products()
for data_product in data_products:
    print(data_product.url)

# Logout
auth.logout()
```

## Example #2 - Creating a project and flight

```python
from datetime import datetime

from d2spy.auth import Auth
from d2spy.workspace import Workspace

# Base URL for D2S instance
base_url = "http://localhost:8000"

# Create an instance of Auth
auth = Auth(base_url)

# Enter your password when prompted
auth.login(email="your_d2s_email@example.com")

# Get active session from auth
session = auth.session

# Create Workspace instance for session
workspace = Workspace(base_url, session)

# Create new project
project = workspace.add_project(
    title="My project",
    description="Project for testing out d2spy project creation.""",
    location={
        "center_x": -86.94416,
        "center_y": 41.44395,
        "geom": "SRID=4326;POLYGON((-86.94441672717005 41.44404961253193, -86.94390178181068 41.44404885476553, -86.94390195544541 41.44384725035913, -86.94441824769912 41.44384953223498, -86.94441824769912 41.44384953223498, -86.94441672717005 41.44404961253193))"
    }
)
print(project)

# Add a flight to new project
flight = project.add_flight(
    aquisition_date=datetime(2022, 6, 4),
    altitude=40,
    side_overlap=85,
    forward_overlap=85,
    sensor="RGB",
    platform="M300"
)
print(flight)

# Logout
auth.logout()
```

## Example #3 - Uploading data products to a flight

```python
from d2spy.auth import Auth
from d2spy.workspace import Workspace

# Base URL for D2S instance
base_url = "http://localhost:8000"

# Create an instance of Auth
auth = Auth(base_url)

# Enter your password when prompted
auth.login(email="your_d2s_email@example.com")

# Get active session from auth
session = auth.session

# Create Workspace instance for session
workspace = Workspace(base_url, session)

# Get specific project by its unique ID
project = workspace.get_project("unique_project_id")

# Get specific flight by its unique ID
flight = project.get_flight("unique_flight_id")

# Upload local RGB orthomosaic GeoTIFF to flight
path_to_tif = "/path/to/tif/on/local/machine/rgb-ortho.tif"
data_product = flight.add_data_product(path_to_tif, data_type="ortho")
print(data_product)
```

::: d2spy.workspace.Workspace
