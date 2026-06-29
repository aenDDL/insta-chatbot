class DomainError(Exception):
    """Base class for domain-level errors."""


class UnauthorizedError(DomainError):
    def __init__(self, details: str):
        super().__init__("User not authorized")
        self.details = details


class ExternalServiceError(DomainError):
    def __init__(self, message: str, details: str):
        super().__init__(message)
        self.message = message
        self.details = details


class ServiceUnavailableError(ExternalServiceError):
    def __init__(self, message: str, details: str):
        super().__init__(message, details)
