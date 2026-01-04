from typing import Optional


class BaseDddError(Exception):
    """
    Root exception for the entire DDD System.
    Enforces a standard message format: "[{Context}] {Layer} Error: {Message}"
    """

    def __init__(
        self, 
        message: str, 
        context_name: str, 
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.context_name = context_name
        self.original_error = original_error

        # Format the final message
        header = f"[{self.context_name}] {self.layer_title} Error"
        final_msg = f"{header}: {self.message}" if self.message else header

        super().__init__(final_msg)

    @property
    def layer_title(self) -> str:
        """
        Override this in subclasses to define the layer name.
        """
        return "System"


# --- Layer Specific Base Errors ---

class GenericDomainError(BaseDddError):
    """
    Base class for all Logic/Business rule violations.
    Usage: raise GenericDomainError("User not found", context_name="Billing")
    """
    @property
    def layer_title(self) -> str:
        return "Domain"


class GenericAppError(BaseDddError):
    """
    Base class for Orchestration failures.
    Usage: raise GenericAppError("UseCase failed", context_name="Billing")
    """
    @property
    def layer_title(self) -> str:
        return "App"


class GenericPortError(BaseDddError):
    """
    Base class for Interface/Translation failures.
    Usage: raise GenericPortError("Mapping failed", context_name="Billing")
    """
    @property
    def layer_title(self) -> str:
        return "Port"


class GenericAdapterError(BaseDddError):
    """
    Base class for Technical/Driver failures.
    Usage: raise GenericAdapterError("DB connection lost", context_name="Billing")
    """
    @property
    def layer_title(self) -> str:
        return "Adapter"