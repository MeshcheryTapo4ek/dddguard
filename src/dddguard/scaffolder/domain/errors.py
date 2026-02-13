from dddguard.shared.helpers.generics import GenericDomainError


class ScaffolderDomainError(GenericDomainError):
    """
    Base exception for Scaffolder Domain.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message=message, context_name="Scaffolder", original_error=original_error)
