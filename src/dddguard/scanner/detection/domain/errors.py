from dddguard.shared.helpers.generics import GenericDomainError


class ImportParsingError(GenericDomainError):
    """
    Failed to parse AST for imports in a specific file.
    """

    def __init__(self, file_path: str, original_error: Exception | None = None):
        msg = f"Failed to parse imports in: {file_path}"
        super().__init__(
            message=msg, context_name="Scanner.Detection", original_error=original_error
        )
