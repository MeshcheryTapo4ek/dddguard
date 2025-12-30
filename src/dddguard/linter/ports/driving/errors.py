from dataclasses import dataclass


@dataclass
class LinterPortError(Exception):
    """Base exception for Linter Port operations."""

    message: str

    def __post_init__(self):
        super().__init__(self.message)
