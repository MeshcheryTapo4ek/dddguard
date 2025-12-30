from dataclasses import dataclass


@dataclass
class ScaffolderDomainError(Exception):
    """Base exception for Scaffolder Domain."""

    message: str

    def __post_init__(self):
        super().__init__(self.message)
