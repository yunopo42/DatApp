class DomainError(Exception):
    """Base class for expected application-domain failures."""


class ResourceNotFoundError(DomainError):
    """Raised when a resource is absent or invisible to the current user."""


class PermissionDeniedError(DomainError):
    """Raised when a workspace member lacks the required role."""


class ConflictError(DomainError):
    """Raised when a requested unique resource already exists."""


class AuthenticationError(DomainError):
    """Raised when credentials or required identity claims are invalid."""


class AuthConfigurationError(DomainError):
    """Raised when managed authentication is not configured."""


class AuthProviderUnavailableError(DomainError):
    """Raised when signing keys cannot be obtained from the auth provider."""
