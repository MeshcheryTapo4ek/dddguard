from dataclasses import dataclass

@dataclass
class LinterAdapterError(Exception):
    """
    Base exception for Linter Driving Adapters.
    Wraps application errors for the Port layer.
    """
    message: str

    def __post_init__(self):
        super().__init__(self.message)