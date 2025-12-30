from dataclasses import dataclass
from pathlib import Path
from typing import List

from dddguard.shared import ConfigVo

from ...app import ScanProjectUseCase, ClassifyTreeUseCase, ScannerAppError
from ...domain import ScanResult

from .response_schema import ScanResponseSchema, ClassifiedNodeSchema


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerController:
    """
    Driving Port: Facade for the Scanner Context.
    """

    scan_use_case: ScanProjectUseCase
    classify_use_case: ClassifyTreeUseCase
    config: ConfigVo

    def scan_project(
        self,
        target_path: Path | None = None,
        whitelist_contexts: List[str] | None = None,
        whitelist_layers: List[str] | None = None,
        dirs_only: bool = False,
        scan_all: bool = False,
        import_depth: int = 0,
    ) -> ScanResponseSchema:
        """
        Executes scanning and returns the Schema with graph data.
        """
        # The absolute root of the source code (e.g. /.../src)
        project_source_root = self.config.project.absolute_source_path
        
        # The specific folder we are focusing on (e.g. /.../src/scanner)
        # If no target provided, we focus on the whole root.
        focus_path = target_path if target_path else project_source_root

        if not focus_path.exists():
            raise FileNotFoundError(f"Target path not found: {focus_path}")

        try:
            result: ScanResult = self.scan_use_case.execute(
                scan_root=project_source_root,
                focus_path=focus_path,
                whitelist_contexts=whitelist_contexts,
                whitelist_layers=whitelist_layers,
                dirs_only=dirs_only,
                scan_all=scan_all,
                import_depth=import_depth,
            )

            hierarchical_dict = result.graph.to_hierarchical_dict()

            all_nodes = result.graph.all_nodes
            visible_nodes = result.graph.visible_nodes
            
            unclassified = sum(
                1 for n in all_nodes if str(n.component_type) == "UNKNOWN"
            )

            return ScanResponseSchema(
                source_tree=result.source_tree,
                dependency_graph=hierarchical_dict,
                context_count=len(hierarchical_dict.keys()),
                file_count=len(all_nodes),
                snapshot_file_count=len(visible_nodes),
                unclassified_count=unclassified,
                success=True,
            )

        except ScannerAppError as e:
            raise e

    def classify_tree(self, target_path: Path | None = None) -> ClassifiedNodeSchema:
        path = target_path if target_path else self.config.project.absolute_source_path
        exclude = self.config.scanner.exclude_dirs
        return self.classify_use_case.execute(path, exclude)