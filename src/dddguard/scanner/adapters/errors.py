from dataclasses import dataclass


@dataclass
class ScannerAdapterError(Exception):
    """
    Base exception for Driving Adapters (e.g. Controller failures).
    Expected to be caught by Driving Ports (CLI).
    """

    message: str

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class FileSystemReadError(Exception):
    """
    Failed to read file from disk (permissions, encoding, etc.).
    Used by Driven Adapters.
    """

    path: str
    original_error: str

    def __post_init__(self):
        super().__init__(f"Could not read file {self.path}: {self.original_error}")
