from typing import Optional
from dddguard.shared.helpers.generics import GenericAdapterError


class ScannerAdapterError(GenericAdapterError):
    """
    Base exception for Scanner Adapters (ACL/Integration).
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            context_name="Scanner",
            original_error=original_error
        )


class GatewayIntegrationError(ScannerAdapterError):
    """
    Raised when an internal gateway (ACL) fails to communicate with a sub-context.
    """
    def __init__(self, gateway_name: str, original_error: Exception):
        super().__init__(
            message=f"Integration failure in {gateway_name}: {str(original_error)}",
            original_error=original_error
        )