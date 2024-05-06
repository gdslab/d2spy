Class used for making API requests to D2S instance.

## Usage

To use this class, first import it into your Python script:

```python
from d2spy.api_client import APIClient
```

Then create an instance of `APIClient`:

```python
client = APIClient(base_url, session)
```

## Example

```python
from d2spy.auth import Auth
from d2spy.api_client import APIClient

# Base URL for D2S instance
base_url = "http://localhost:8000"

# Create an instance of Auth
auth = Auth(base_url)

# Enter your password when prompted
auth.login(email="your_d2s_email@example.com")

# Get active session from auth
session = auth.session

# Create APIClient instance for session
client = APIClient(base_url, session)

# Make health check request to D2S instance
response = client.make_get_request("/api/v1/health")
print(response.json())

# Logout
auth.logout()
```

::: d2spy.api_client.APIClient
