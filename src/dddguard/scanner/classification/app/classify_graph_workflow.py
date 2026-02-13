import logging
from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import ArchetypeType, CodeGraph

from .identify_component_uc import IdentifyComponentUseCase

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifyGraphWorkflow:
    """
    Workflow: Graph Classification.

    Orchestrates the transformation of a 'LINKED' CodeGraph into a 'CLASSIFIED' CodeGraph.

    **Mechanism:**
    Iterates over every node in the graph and delegates to `IdentifyComponentUseCase`.
    This operation is **mutative**: it updates the `passport` attribute of existing nodes in-place.
    """

    identifier_use_case: IdentifyComponentUseCase

    def __call__(self, graph: CodeGraph, source_dir: Path) -> CodeGraph:
        """
        Executes the classification workflow.

        :param graph: The CodeGraph with populated imports (Linked state).
        :param source_dir: Absolute path to the project root (used for path resolution).
        :return: The same CodeGraph instance, but with classified nodes.
        """
        logger.info("Starting architectural classification of %d nodes...", len(graph.nodes))

        classified_count = 0
        unknown_count = 0

        for node in graph.nodes.values():
            # 1. Resolve Physical Path
            # Ideally, nodes already have a file_path. If not, we reconstruct it from the logical path.
            target_path = node.file_path
            if not target_path:
                # Fallback: src.domain.model -> src/domain/model.py
                # Note: This implies a standard structure and might fail for custom layouts.
                rel_path_str = node.path.replace(".", "/") + ".py"
                target_path = source_dir / rel_path_str

            # 2. Identify
            passport = self.identifier_use_case(file_path=target_path, source_dir=source_dir)

            # 3. Mutate Node
            node.classify(passport)

            # Metrics
            if passport.component_type == ArchetypeType.UNKNOWN:
                unknown_count += 1
            else:
                classified_count += 1

        logger.info(
            "Classification complete. Classified: %d, Unknown: %d",
            classified_count,
            unknown_count,
        )
        return graph
