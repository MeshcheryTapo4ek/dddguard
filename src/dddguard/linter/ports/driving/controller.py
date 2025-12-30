from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from dddguard.shared import ConfigVo
from dddguard.shared.domain.policies.access_policy import (
    INTERNAL_ACCESS_MATRIX,
    PUBLIC_LAYERS,
    OUTBOUND_LAYERS,
)

from ...app import CheckProjectUseCase, LinterAppError
from .schemas import LinterResponseSchema, ViolationSchema
from .errors import LinterPortError


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterController:
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
        # 1. Input Logic
        target_path = path if path else self.config.project.absolute_source_path

        if not target_path.exists():
            # In a Port, we might throw a domain-agnostic error or return a failure schema
            # Here we raise an error expected by the CLI adapter wrapper
            raise FileNotFoundError(f"Path not found: {target_path}")

        try:
            # 2. Application Invocation
            report = self.use_case.execute(target_path)

            # 3. Output Mapping (Domain VO -> Presentation Schema)
            dtos = [
                ViolationSchema(
                    rule_id=v.rule_id,
                    message=v.message,
                    source=v.source_module,
                    target=v.target_module,
                    severity=v.severity,
                    target_context=v.target_context,
                )
                for v in report.violations
            ]

            return LinterResponseSchema(
                total_scanned=report.total_files_scanned,
                violations=dtos,
                success=not bool(dtos),
            )

        except LinterAppError as e:
            # Wrap Application errors into Port errors
            raise LinterPortError(e.message) from e

    def get_rules_matrix(self) -> Dict[str, Any]:
        """
        Exposes Domain Rules to the Adapter (for visualization purposes).
        """
        return {
            "internal": INTERNAL_ACCESS_MATRIX,
            "public": PUBLIC_LAYERS,
            "outbound": OUTBOUND_LAYERS,
        }
