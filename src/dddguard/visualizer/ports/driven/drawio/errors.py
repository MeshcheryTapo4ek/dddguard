from dddguard.shared.helpers.generics import GenericAdapterError


class FileWriteError(GenericAdapterError):
    """
    Raised when the renderer fails to write the XML file to disk.
    """
    def __init__(self, path: str, original_error: Exception):
        super().__init__(
            message=f"IO Error writing to {path}: {str(original_error)}",
            context_name="Visualizer",
            original_error=original_error
        )