from dataclasses import dataclass
from pathlib import Path
from typing import List

from dddguard.scanner import ScanProjectUseCase, ScannerAppError
from ...domain import LinterReportVo, ViolationVo, RuleEngineService, LinterDomainError
from ..errors import AnalysisExecutionError, LinterAppError


@dataclass(frozen=True, kw_only=True, slots=True)
class CheckProjectUseCase:
    """
    App Service: Orchestrates the linting process.
    Catches errors from Scanner and internal Domain services.
    """
    scan_project: ScanProjectUseCase
    rule_engine: RuleEngineService

    def execute(self, root_path: Path) -> LinterReportVo:
        try:
            # 1. Get the Domain Graph (External Context Call)
            # Scanner might raise  (ScannerAppError)
            scan_result = self.scan_project.execute(root_path)
            graph = scan_result.graph

            all_violations: List[ViolationVo] = []
            
            # 2. Iterate cleanly over object nodes
            for node in graph.all_nodes:
                for link in node.imports:
                    # Rule Engine (Domain) might raise LinterDomainError
                    violations = self.rule_engine.check_dependency(node, link)
                    all_violations.extend(violations)

            return LinterReportVo(
                total_files_scanned=len(graph.nodes), 
                violations=all_violations
            )

        except ScannerAppError as e:
            # Wrap external context error into local App error
            raise AnalysisExecutionError("scanning", f"Scanner context failed: {e}") from e
        
        except LinterDomainError as e:
            # Wrap internal domain error
            raise AnalysisExecutionError("rule_checking", f"Domain rule error: {e}") from e
            
        except Exception as e:
            # Wrap unexpected/adapter errors
            raise AnalysisExecutionError("unknown", str(e)) from e