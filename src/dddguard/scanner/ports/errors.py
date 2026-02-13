from dddguard.shared.helpers.generics import GenericDrivingPortError


class ScannerPortError(GenericDrivingPortError):
    """Base exception for Scanner Driving Ports layer."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(
            message=message,
            context_name="Scanner",
            original_error=original_error,
        )


class InvalidScanPathError(ScannerPortError):
    """Raised when the target path for scanning does not exist or is invalid."""

    def __init__(self, path: str):
        super().__init__(f"Target path not found or inaccessible: {path}")
