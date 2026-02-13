from dddguard.shared.helpers.generics import GenericDomainError


class LinterDomainError(GenericDomainError):
    """
    Base exception for Linter Domain Logic.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message=message, context_name="Linter", original_error=original_error)


class RuleDefinitionError(LinterDomainError):
    """
    Raised when the rule matrix structure is invalid.
    """

    def __init__(self, rule_id: str):
        super().__init__(f"Invalid rule definition detected for ID: {rule_id}")
