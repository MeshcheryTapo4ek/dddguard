class BaseDddError(Exception):
    """
    Root exception for the entire DDD System.
    Enforces a standard message format: "[{Context}] {Layer} Error: {Message}"
    """

    def __init__(
        self,
        message: str,
        context_name: str,
        original_error: Exception | None = None,
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
    Base class for Port (interface/translation) failures.
    Kept for backward compatibility. Prefer Driving/Driven variants.
    """

    @property
    def layer_title(self) -> str:
        return "Port"


class GenericDrivingPortError(GenericPortError):
    """
    Base class for Driving Port failures (Facades, Schemas, Dispatchers).
    These are entry points that external actors use to invoke the context.
    """

    @property
    def layer_title(self) -> str:
        return "Driving Port"


class GenericDrivenPortError(GenericPortError):
    """
    Base class for Driven Port failures (Repositories, Gateways, ACLs, Publishers).
    These are exit points that the context uses to reach external systems.
    """

    @property
    def layer_title(self) -> str:
        return "Driven Port"


class GenericAdapterError(BaseDddError):
    """
    Base class for Adapter (technical/driver) failures.
    Kept for backward compatibility. Prefer Driving/Driven variants.
    """

    @property
    def layer_title(self) -> str:
        return "Adapter"


class GenericDrivingAdapterError(GenericAdapterError):
    """
    Base class for Driving Adapter failures (Controllers, CLI handlers,
    Consumers, Wizards). These translate external signals into app calls.
    """

    @property
    def layer_title(self) -> str:
        return "Driving Adapter"


class GenericDrivenAdapterError(GenericAdapterError):
    """
    Base class for Driven Adapter failures (DB engines, HTTP clients,
    message producers, file system I/O). These implement driven port contracts.
    """

    @property
    def layer_title(self) -> str:
        return "Driven Adapter"
