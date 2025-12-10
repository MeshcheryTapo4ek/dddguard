from dataclasses import dataclass

@dataclass
class LinterDomainError(Exception):
    """Base exception for Linter Domain Logic."""
    message: str

    def __post_init__(self):
        super().__init__(self.message)


@dataclass
class RuleDefinitionError(LinterDomainError):
    """Raised when the rule matrix structure is invalid."""
    rule_id: str

    def __post_init__(self):
        super().__init__(f"Invalid rule definition detected for ID: {self.rule_id}")