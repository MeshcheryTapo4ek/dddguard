from typing import Optional
from dddguard.shared.helpers.generics import GenericAppError


class ScaffolderAppError(GenericAppError):
    """
    Base exception for Scaffolder App Layer.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Scaffolder",
            original_error=original_error
        )


class InitializationError(ScaffolderAppError):
    """
    Raised when project initialization fails.
    """
    def __init__(self, project_name: str, reason: str, original_error: Optional[Exception] = None):
        msg = f"Failed to initialize project '{project_name}': {reason}"
        super().__init__(message=msg, original_error=original_error)