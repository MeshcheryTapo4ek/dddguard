from dataclasses import dataclass

@dataclass
class VisualizerDomainError(Exception):
    """Base exception for Visualizer Domain Layer."""
    message: str
    
    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class LayoutCalculationError(VisualizerDomainError):
    """Raised when the layout algorithm fails to place nodes."""
    context_name: str

    def __post_init__(self):
        super().__init__(f"Failed to calculate layout for context: {self.context_name}")