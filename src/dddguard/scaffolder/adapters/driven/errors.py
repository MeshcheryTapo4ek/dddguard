from dataclasses import dataclass, field

@dataclass
class ScaffolderAdapterError(Exception):
    """Base exception for Scaffolder Infrastructure."""
    message: str

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class TemplateNotFoundError(ScaffolderAdapterError):
    """Raised when a specific blueprint cannot be found."""
    blueprint_name: str
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Blueprint '{self.blueprint_name}' not found."
        super().__post_init__()


@dataclass
class TemplateRenderingError(ScaffolderAdapterError):
    """Raised when Jinja fails to render a template."""
    template_name: str
    error_details: str
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Failed to render template '{self.template_name}': {self.error_details}"
        super().__post_init__()


@dataclass
class FileWriteError(ScaffolderAdapterError):
    """Raised when writing to disk fails."""
    path: str
    error_details: str
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Could not write file to '{self.path}': {self.error_details}"
        super().__post_init__()