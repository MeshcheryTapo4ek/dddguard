from dataclasses import dataclass, field


@dataclass
class ScannerAppError(Exception):
    """
    Base exception for Scanner App Layer.
    Expected to be caught by the Presentation Layer (CLI/API).
    """

    message: str

    def __post_init__(self):
        # Here super() is Exception (not a dataclass), so it's safe
        super().__init__(self.message)


@dataclass
class ProjectScanError(ScannerAppError):
    """
    Critical failure executing the scanning process.
    """

    root_path: str
    details: str = ""

    # Exclude 'message' from __init__ because we calculate it internally
    message: str = field(init=False)

    def __post_init__(self):
        self.message = (
            f"Failed to scan project at: {self.root_path}. Reason: {self.details}"
        )

        # FIX: Call Exception.__init__ directly to bypass
        # ScannerAppError's generated __init__ which would re-trigger __post_init__
        Exception.__init__(self, self.message)


@dataclass
class ClassificationError(ScannerAppError):
    """
    Failed to classify a specific file logic.
    """

    file_path: str
    # Exclude 'message' from __init__
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Could not classify file: {self.file_path}"

        # FIX: Same recursion prevention here
        Exception.__init__(self, self.message)
