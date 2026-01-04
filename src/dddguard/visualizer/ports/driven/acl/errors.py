from dddguard.shared.helpers.generics import GenericAdapterError


class ScannerIntegrationError(GenericAdapterError):
    """
    Raised when the connection to the Scanner Context fails.
    """
    def __init__(self, original_error: Exception):
        super().__init__(
            message=f"Failed to communicate with Scanner: {str(original_error)}",
            context_name="Visualizer",
            original_error=original_error
        )