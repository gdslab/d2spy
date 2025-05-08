try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version("d2spy")
except PackageNotFoundError:
    __version__ = "unknown"
