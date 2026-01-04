from typing import Optional
from dddguard.shared.helpers.generics import GenericAppError


class ProjectScanError(GenericAppError):
    """
    Critical failure executing the scanning process.
    """
    def __init__(
        self, 
        root_path: str, 
        details: str = "", 
        original_error: Optional[Exception] = None
    ):
        msg = f"Failed to scan project at: {root_path}. Reason: {details}"
        super().__init__(
            message=msg, 
            context_name="Scanner.Detection", 
            original_error=original_error
        )