class PackagingRestApiError(Exception):
    """Base packaging REST API Error"""


class ShellNotFoundException(PackagingRestApiError):
    pass


class FeatureUnavailable(PackagingRestApiError):
    pass
