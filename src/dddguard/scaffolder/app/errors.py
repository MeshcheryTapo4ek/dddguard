from dataclasses import dataclass, field

@dataclass
class ScaffolderAppError(Exception):
    """Base exception for Scaffolder App Layer."""
    message: str
    
    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class InitializationError(ScaffolderAppError):
    """Raised when project initialization fails."""
    project_name: str
    reason: str
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Failed to initialize project '{self.project_name}': {self.reason}"
        super().__post_init__()