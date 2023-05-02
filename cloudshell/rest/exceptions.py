class PackagingRestApiError(Exception):
    """Base packaging REST API Error."""


class ShellNotFound(PackagingRestApiError):
    pass


class FeatureUnavailable(PackagingRestApiError):
    pass


class LoginFailedError(PackagingRestApiError):
    pass
