from dddguard.shared.helpers.generics import GenericAppError


class VisualizerAppError(GenericAppError):
    """
    Base exception for Visualizer App Layer.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message=message, context_name="Visualizer", original_error=original_error)


class RenderingError(VisualizerAppError):
    """
    Raised when the rendering process (Adapter) fails.
    """

    def __init__(self, output_path: str, original_error: Exception):
        msg = f"Failed to render diagram to {output_path}: {original_error!s}"
        super().__init__(message=msg, original_error=original_error)


class LayoutError(VisualizerAppError):
    """
    Raised when the domain layout service fails.
    """

    def __init__(self, original_error: Exception):
        msg = f"Layout calculation failed: {original_error!s}"
        super().__init__(message=msg, original_error=original_error)
