try:
    from ._version import version_tuple, version
except ImportError:
    version = "0.0.0"
    version_tuple = (0, 0, 0)

__all__ = ["version", "version_tuple"]
