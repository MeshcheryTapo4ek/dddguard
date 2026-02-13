from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph

from ..domain import (
    LinterDomainError,
    LinterReport,
    RuleEngineService,
    ViolationEvent,
)
from .errors import AnalysisExecutionError
from .interfaces import IScannerGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class CheckProjectUseCase:
    """
    App Service: Orchestrates the linting process.
    """

    scanner_gateway: IScannerGateway
    rule_engine: RuleEngineService

    def execute(self, root_path: Path) -> LinterReport:
        try:
            # 1. Get Graph via ACL
            graph: CodeGraph = self.scanner_gateway.get_project_graph(root_path)

            # 2. Validate all nodes against architectural rules
            all_violations: list[ViolationEvent] = []
            for node in graph.nodes.values():
                violations = self.rule_engine.check_node(node, graph)
                all_violations.extend(violations)

            return LinterReport(
                total_files_scanned=len(graph.nodes),
                violations=tuple(all_violations),
            )

        except LinterDomainError as e:
            raise AnalysisExecutionError(step="rule_checking", original_error=e) from e

        except Exception as e:
            raise AnalysisExecutionError(step="unknown", original_error=e) from e
