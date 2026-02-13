from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import (
    CROSS_CONTEXT_INBOUND_ALLOWED,
    CROSS_CONTEXT_OUTBOUND_ALLOWED,
    FRACTAL_DOWNSTREAM_ALLOWED,
    FRACTAL_DOWNSTREAM_FORBIDDEN,
    FRACTAL_UPSTREAM_ALLOWED,
    FRACTAL_UPSTREAM_FORBIDDEN,
    INTERNAL_ACCESS_MATRIX,
    ConfigVo,
)
from dddguard.shared.helpers.generics import GenericDrivingPortError

from ...app import CheckProjectUseCase, LinterAppError
from .schemas import (
    FractalRulesSchema,
    LinterResponseSchema,
    RulesMatrixSchema,
    ViolationSchema,
)


class LinterPortError(GenericDrivingPortError):
    """
    Base exception for Linter Port operations.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message=message, context_name="Linter", original_error=original_error)


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterFacade:
    """
    Driving Port: Bridges the outside world (CLI) to the Linter Application Logic.
    Responsible for Input Validation, Orchestration, and Output Mapping (Domain -> Schema).
    """

    use_case: CheckProjectUseCase
    config: ConfigVo

    def lint_project(self, path: Path | None = None) -> LinterResponseSchema:
        """
        Executes the linting logic for a given path or the configured project root.
        """
        # 1. Input Validation
        target_path = path or self.config.project.absolute_source_path

        if target_path is None:
            raise LinterPortError(
                "No target path provided and no source_dir configured. "
                "Please configure 'project.source_dir' in config.yaml."
            )

        if not target_path.exists():
            raise LinterPortError(f"Target path does not exist: {target_path}")

        try:
            # 2. Application Invocation
            report = self.use_case.execute(target_path)

            # 3. Output Mapping (Domain VO -> Presentation Schema)
            violations = tuple(
                ViolationSchema(
                    rule_name=v.rule_name,
                    message=v.message,
                    source=v.source_module,
                    target=v.target_module,
                    severity=v.severity,
                    target_context=v.target_context,
                )
                for v in report.violations
            )

            return LinterResponseSchema(
                total_scanned=report.total_files_scanned,
                violations=violations,
                success=len(violations) == 0,
            )

        except LinterAppError as e:
            raise LinterPortError(e.message, original_error=e) from e

    def get_rules_matrix(self) -> RulesMatrixSchema:
        """
        Exposes all 13 Domain Rules to the Adapter (for visualization purposes).
        Covers Internal (1-7), Fractal (8-9), Cross-Context (10-11).
        Scope Isolation (12-13) is rendered from static descriptions.
        """
        return RulesMatrixSchema(
            internal=INTERNAL_ACCESS_MATRIX,
            fractal=FractalRulesSchema(
                upstream_allowed=FRACTAL_UPSTREAM_ALLOWED,
                upstream_forbidden=FRACTAL_UPSTREAM_FORBIDDEN,
                downstream_allowed=FRACTAL_DOWNSTREAM_ALLOWED,
                downstream_forbidden=FRACTAL_DOWNSTREAM_FORBIDDEN,
            ),
            outbound_allowed=CROSS_CONTEXT_OUTBOUND_ALLOWED,
            inbound_allowed=CROSS_CONTEXT_INBOUND_ALLOWED,
        )
