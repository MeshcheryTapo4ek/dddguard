from dataclasses import dataclass

@dataclass
class VisualizerAppError(Exception):
    """
    Base exception for Visualizer App Layer.
    """
    message: str = "" 

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class RenderingError(VisualizerAppError):
    """Raised when the rendering process (Adapter) fails."""
    output_path: str = ""
    original_error: str = ""

    def __post_init__(self):
        self.message = f"Failed to render diagram to {self.output_path}: {self.original_error}"
        super().__post_init__()


@dataclass
class LayoutError(VisualizerAppError):
    """Raised when the domain layout service fails."""
    original_error: str = ""

    def __post_init__(self):
        self.message = f"Layout calculation failed: {self.original_error}"
        super().__post_init__()