from typing import Optional
from dddguard.shared.helpers.generics import GenericDomainError


class LayoutCalculationError(GenericDomainError):
    """
    Raised when the layout algorithm fails to place nodes.
    """
    def __init__(self, context_name: str, original_error: Optional[Exception] = None):
        msg = f"Failed to calculate layout for context: {context_name}"
        super().__init__(
            message=msg,
            context_name="Visualizer",
            original_error=original_error
        )