from pathlib import Path
from typing import Protocol

from dddguard.shared.domain import CodeGraph, ScannerConfig


class IDetectionGateway(Protocol):
    """
    ACL: Interface to the Detection Bounded Context (Physical Analysis).
    """

    def scan(
        self,
        scanner_config: ScannerConfig,
        target_path: Path,
        scan_all: bool,
    ) -> CodeGraph:
        """
        Triggers physical scanning: Walking -> AST Parsing -> Import Resolution.
        Returns a LINKED CodeGraph (Nodes exist, imports resolved, but NO architecture info).
        """
        ...


class IClassificationGateway(Protocol):
    """
    ACL: Interface to the Classification Bounded Context (Architectural Analysis).
    """

    def classify(self, graph: CodeGraph, source_dir: Path | None = None) -> CodeGraph:
        """
        Takes a LINKED CodeGraph and mutates it into a CLASSIFIED CodeGraph.
        Assigns 'ComponentPassport' to every node.

        :param source_dir: Contextual root for calculating relative paths during classification.
        """
        ...
