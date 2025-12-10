from dataclasses import dataclass, field

@dataclass
class ScannerDomainError(Exception):
    """
    Base exception for Scanner Domain Layer.
    """
    message: str
    
    def __post_init__(self):
        Exception.__init__(self, self.message)


@dataclass
class ImportParsingError(ScannerDomainError):
    """
    Failed to parse AST for imports in a specific file.
    """
    file_path: str
    message: str = field(init=False)
    
    def __post_init__(self):
        self.message = f"Failed to parse imports in: {self.file_path}"
        Exception.__init__(self, self.message)


@dataclass
class HeuristicIdentificationError(ScannerDomainError):
    """
    Failed to identify component type based on available tokens.
    """
    token: str
    message: str = field(init=False)

    def __post_init__(self):
        self.message = f"Could not identify component by token: {self.token}"
        Exception.__init__(self, self.message)