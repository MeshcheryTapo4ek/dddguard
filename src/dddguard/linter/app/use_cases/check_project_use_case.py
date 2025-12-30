from dataclasses import dataclass
from pathlib import Path
from typing import List

from ...domain import (
    LinterReportVo,
    ViolationVo,
    RuleEngineService,
    LinterDomainError,
    ScannedNodeVo,
)
from ..interfaces import IScannerGateway
from ..errors import AnalysisExecutionError


@dataclass(frozen=True, kw_only=True, slots=True)
class CheckProjectUseCase:
    """
    App Service: Orchestrates the linting process.
    """

    scanner_gateway: IScannerGateway
    rule_engine: RuleEngineService

    def execute(self, root_path: Path) -> LinterReportVo:
        try:
            # 1. Get Pure Domain Nodes via ACL
            nodes: List[ScannedNodeVo] = self.scanner_gateway.get_project_nodes(
                root_path
            )

            all_violations: List[ViolationVo] = []

            # 2. Iterate
            for node in nodes:
                for link in node.imports:
                    # Rule Engine now accepts ScannedNodeVo/ScannedImportVo
                    violations = self.rule_engine.check_dependency(node, link)
                    all_violations.extend(violations)

            return LinterReportVo(
                total_files_scanned=len(nodes), violations=all_violations
            )

        except LinterDomainError as e:
            raise AnalysisExecutionError(
                "rule_checking", f"Domain rule error: {e}"
            ) from e

        except Exception as e:
            raise AnalysisExecutionError("unknown", str(e)) from e
