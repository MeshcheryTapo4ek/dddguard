from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import (
    CodeGraph,
)

from ...app import ClassifyGraphWorkflow


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationFacade:
    """
    Driving Port: Facade for the Classification Context.
    Directly returns Domain Objects (which are now Shared Types).
    """

    graph_workflow: ClassifyGraphWorkflow

    def classify_graph(self, graph: CodeGraph, source_dir: Path | None = None) -> CodeGraph:
        """
        Takes a physical CodeGraph and applies architectural classification.

        :param graph: The graph to classify.
        :param source_dir: the project root.
                             If None, uses the configured absolute source path.
                             This is crucial for partial scans (scandir) where the
                             target path determines the relative root.
        """
        return self.graph_workflow(graph=graph, source_dir=source_dir)  # type: ignore[arg-type]
