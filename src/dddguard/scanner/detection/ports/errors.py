from typing import Optional
from dddguard.shared.helpers.generics import GenericPortError


class DetectionPortError(GenericPortError):
    """
    Base exception for Scanner.Detection Ports layer.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Scanner.Detection",
            original_error=original_error
        )


class InvalidScanPathError(DetectionPortError):
    """
    Raised when the target path for scanning does not exist or is invalid.
    """
    def __init__(self, path: str):
        super().__init__(f"Target path not found or inaccessible: {path}")