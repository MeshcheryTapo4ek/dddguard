from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph, ScannerConfig

from ...domain import (
    GraphExpansionService,
    GraphFilteringService,
)
from ..interfaces import IClassificationGateway, IDetectionGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class RunScanUseCase:
    """
    Macro UseCase: Orchestrates the End-to-End Scanning Pipeline.

    This is the main entry point for generating a filtered, classified architecture graph.

    **Architectural Strategy: "Global Awareness, Local Focus"**
    To accurately resolve imports and cross-context dependencies, the scanner **always**
    ingests the entire project source tree physically (Detection Phase).
    It then logically narrows down the visibility to the requested `focus_path` (Filtering Phase).

    **Pipeline Stages:**
    1.  **Detection:** Parse AST and resolve imports for the *entire* project (Linkage Integrity).
    2.  **Classification:** Assign architectural passports to *all* nodes.
    3.  **Filtering:** Hide nodes outside the `focus_path` or exclude specific Layers/Contexts.
    4.  **Expansion:** Recursively reveal hidden dependencies of visible nodes (Import Depth).
    5.  **Pruning:** Finalize the graph state for rendering.
    """

    detection_gateway: IDetectionGateway
    classification_gateway: IClassificationGateway

    def __call__(
        self,
        scanner_config: ScannerConfig,
        source_dir: Path,
        scan_all: bool = False,
        import_depth: int = 0,
        whitelist_layers: list[str] | None = None,
        whitelist_contexts: list[str] | None = None,
        include_assets: bool = True,
    ) -> CodeGraph:
        """
        Executes the scan.

        :param source_dir:
            The absolute path to the project source root.
            This is the single anchor point for all scanning operations.

        :param scan_all:
            If `True`, scans all text files (Asset Mode).
            If `False`, scans only Python code (Strict Mode).

        :param import_depth:
            How many levels of dependencies to reveal.
            - `0`: Strict containment (show only what is inside `focus_path`).
            - `1`: Show immediate dependencies of focused nodes (even if outside `focus_path`).
            - `N`: Show N levels of dependency chain.

        :param whitelist_layers:
            List of Layer names (e.g., `["domain", "app"]`).
            Nodes belonging to other layers will be hidden. `None` = Allow All.

        :param whitelist_contexts:
            List of Context names (e.g., `["billing", "shared", "root"]`).
            Nodes from other Bounded Contexts will be hidden. `None` = Allow All.
            Explicitly listing 'root' or 'shared' here will make them visible.

        :param include_assets:
            If `False`, filters out non-code components (ArchetypeType.ASSET).

        :return: A populated `CodeGraph` where nodes are marked as `FINALIZED` (visible) or not.
        """

        # 1. DETECT (Ingest & Link - Full Project)
        # Returns a graph with physical nodes and raw import strings resolved to node IDs.
        detected_graph = self.detection_gateway.scan(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=scan_all,
        )

        # 2. CLASSIFY (Assign Passports - Full Project)
        # Mutates the graph: Nodes go from LINKED -> CLASSIFIED state.
        classified_graph = self.classification_gateway.classify(
            graph=detected_graph,
            source_dir=source_dir,
        )

        # 3. FILTER (Narrowing Phase)
        # Apply subtractive logic: "What should be hidden?"
        # Returns a set of Node IDs (Paths) that survived the filters.
        initial_visible = GraphFilteringService.determine_initial_focus(
            graph=classified_graph,
            focus_path=source_dir,
            whitelist_layers=whitelist_layers,
            whitelist_contexts=whitelist_contexts,
            include_assets=include_assets,
        )

        # 4. EXPAND (Discovery Phase)
        # Apply additive logic: "What hidden nodes are needed by visible nodes?"
        expanded_visible = GraphExpansionService.expand(
            graph=classified_graph,
            initial_visible=initial_visible,
            depth=import_depth,
        )

        # 5. PRUNE (Finalize State)
        # Sets the `.status = FINALIZED` on visible nodes.
        GraphFilteringService.prune_graph(
            graph=classified_graph,
            visible_modules=expanded_visible,
        )

        return classified_graph
