try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError


class PackagingRestApiError(Exception):
    """Base packaging REST API Error."""


class ShellNotFoundException(PackagingRestApiError):
    pass


class FeatureUnavailable(PackagingRestApiError):
    pass


class LoginFailedError(PackagingRestApiError, HTTPError):
    pass
