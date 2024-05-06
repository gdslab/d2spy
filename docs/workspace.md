Class for working with D2S data.

## Usage

To use this class, first import it into your Python script:

```python
from d2spy.workspace import Workspace
```

Then create an instance of `Workspace`:

```python
workspace = Workspace(base_url, session)
```

## Example

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

# Logout
auth.logout()
```

::: d2spy.workspace.Workspace
