from dataclasses import dataclass


@dataclass
class VisualizerAdapterError(Exception):
    """Base exception for Visualizer Adapters."""

    message: str

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class FileWriteError(VisualizerAdapterError):
    """Raised when writing the XML file to disk fails."""

    path: str
    details: str

    def __post_init__(self):
        super().__init__(f"Could not write to file {self.path}: {self.details}")
