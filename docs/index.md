# Homepage

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Codeblock example

```py
import d2spy

def login(username: str, password: str) -> User:
    user = d2spy.auth.login(username, password)
    if not user:
        raise Exception("Unable to login")
    return user
```

## Title example

```py title="auth.py"
import d2spy

def login(username: str, password: str) -> User:
    user = d2spy.auth.login(username, password)
    if not user:
        raise Exception("Unable to login")
    return user
```

## Line no example

```py linenums="1"
import d2spy

def login(username: str, password: str) -> User:
    user = d2spy.auth.login(username, password)
    if not user:
        raise Exception("Unable to login")
    return user
```

## Highlight example

```py linenums="1" hl_lines="5-6"
import d2spy

def login(username: str, password: str) -> User:
    user = d2spy.auth.login(username, password)
    if not user:
        raise Exception("Unable to login")
    return user
```

## Icons and emojis example

:smile:

:fontawesome-regular-face-laugh-wink:

:fontawesome-brands-twitter:{ .twitter }

:octicons-heart-fill-24:{ .heart }

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
