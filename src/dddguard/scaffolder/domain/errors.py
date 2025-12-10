class ScaffolderDomainError(Exception):
    """Base exception for Scaffolder Domain."""
    pass

class TemplateRenderingError(ScaffolderDomainError):
    """Raised when Jinja2 fails to render a template."""
    def __init__(self, template_id: str, reason: str):
        self.template_id = template_id
        self.reason = reason
        super().__init__(f"Failed to render template '{template_id}': {reason}")