from dddguard.shared.helpers.generics import GenericAppError


class LinterAppError(GenericAppError):
    """
    Base exception for Linter Application Layer.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message=message, context_name="Linter", original_error=original_error)


class AnalysisExecutionError(LinterAppError):
    """
    Raised when the analysis process fails unexpectedly.
    """

    def __init__(self, step: str, original_error: Exception):
        msg = f"Failed to execute analysis step '{step}': {original_error!s}"
        super().__init__(message=msg, original_error=original_error)
