Class used for handling authentication with D2S instance.

## Usage

To use this class, first import it into your Python script:

```python
from d2spy.auth import Auth
```

Then create an instance of `Auth`:

```python
auth = Auth(host="http://localhost:8000")
```

## Example

```python
from d2spy.auth import Auth

# Create an instance of Auth
auth = Auth("http://localhost:8000")

# Enter your password when prompted
user = auth.login(email="your_d2s_email@example.com")
print(user)

# Logout
auth.logout()
```

::: d2spy.auth.Auth
