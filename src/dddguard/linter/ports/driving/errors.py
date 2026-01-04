from typing import Optional
from dddguard.shared.helpers.generics import GenericPortError


class LinterPortError(GenericPortError):
    """
    Base exception for Linter Port operations.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Linter",
            original_error=original_error
        )