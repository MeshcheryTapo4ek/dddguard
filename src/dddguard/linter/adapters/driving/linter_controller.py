from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from dddguard.shared import ConfigVo
from dddguard.shared.assets import (
    INTERNAL_ACCESS_MATRIX,
    PUBLIC_LAYERS,
    OUTBOUND_LAYERS,
)

from ...app import CheckProjectUseCase, LinterAppError
from ...dto.driven import LinterResponseDto, ViolationDto

from .errors import LinterAdapterError


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterController:
    """
    Driving Adapter: Bridges CLI and Application Logic.
    Handles exception mapping (App -> Adapter) and DTO conversion.
    """
    use_case: CheckProjectUseCase
    config: ConfigVo

    def lint_project(self, path: Path | None = None) -> LinterResponseDto:
        # 1. Resolve Path
        target_path = path if path else self.config.project.absolute_source_path
        
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")

        try:
            # 2. Execute Application Logic
            report = self.use_case.execute(target_path)

            # 3. Map Domain VO -> Response DTO
            dtos = [
                ViolationDto(
                    rule_id=v.rule_id,
                    message=v.message,
                    source=v.source_module,
                    target=v.target_module,
                    severity=v.severity,
                    target_context=v.target_context 
                )
                for v in report.violations
            ]

            return LinterResponseDto(
                total_scanned=report.total_files_scanned,
                violations=dtos,
                success=not bool(dtos)
            )

        except LinterAppError as e:
            raise LinterAdapterError(e.message) from e

    def get_rules_matrix(self) -> Dict[str, Any]:
        """
        Exposes Domain Rules to the Port.
        The Port calls this method instead of importing Domain constants directly.
        """
        return {
            "internal": INTERNAL_ACCESS_MATRIX,
            "public": PUBLIC_LAYERS,
            "outbound": OUTBOUND_LAYERS,
        }