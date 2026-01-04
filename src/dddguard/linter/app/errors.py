from typing import Optional
from dddguard.shared.helpers.generics import GenericAppError


class LinterAppError(GenericAppError):
    """
    Base exception for Linter Application Layer.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Linter",
            original_error=original_error
        )


class AnalysisExecutionError(LinterAppError):
    """
    Raised when the analysis process fails unexpectedly.
    """
    def __init__(self, step: str, original_error: Exception):
        msg = f"Failed to execute analysis step '{step}': {str(original_error)}"
        super().__init__(message=msg, original_error=original_error)


class ScannerAppError(GenericAppError):
    """
    Base exception for Scanner App Layer (Used in Linter context as reference).
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Scanner", # Note context name
            original_error=original_error
        )