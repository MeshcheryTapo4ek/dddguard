from dddguard.shared.helpers.generics import GenericAdapterError


class ScannerIntegrationError(GenericAdapterError):
    """
    Raised when the connection to the Scanner Context fails.
    Wraps external errors to protect the Linter Domain.
    """
    def __init__(self, original_error: Exception):
        msg = f"Failed to communicate with Scanner: {str(original_error)}"
        super().__init__(
            message=msg,
            context_name="Linter",
            original_error=original_error
        )