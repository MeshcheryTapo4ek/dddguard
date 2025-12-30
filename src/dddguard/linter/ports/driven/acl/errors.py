from dataclasses import dataclass


@dataclass
class ScannerIntegrationError(Exception):
    """
    Raised when the connection to the Scanner Context fails.
    Wraps external errors to protect the Linter Domain.
    """

    original_error: str

    def __post_init__(self):
        super().__init__(f"Failed to communicate with Scanner: {self.original_error}")
