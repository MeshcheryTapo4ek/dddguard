from typing import Optional
from dddguard.shared.helpers.generics import GenericPortError


class VisualizerPortError(GenericPortError):
    """
    Base exception for Visualizer Port operations.
    Replaces the old VisualizerAdapterError.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Visualizer",
            original_error=original_error
        )