from dataclasses import dataclass, field


@dataclass
class LinterAppError(Exception):
    """Base exception for Linter Application Layer."""

    message: str

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class AnalysisExecutionError(LinterAppError):
    """Raised when the analysis process fails unexpectedly."""

    step: str
    original_error: str

    message: str = field(init=False)

    def __post_init__(self):
        self.message = (
            f"Failed to execute analysis step '{self.step}': {self.original_error}"
        )
        Exception.__init__(self, self.message)


@dataclass
class ScannerAppError(Exception):
    """
    Base exception for Scanner App Layer.
    Expected to be caught by the Presentation Layer (CLI/API).
    """

    message: str

    def __post_init__(self):
        super().__init__(self.message)
