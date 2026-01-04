from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from dddguard.shared import ConfigVo

from ...app import ScanProjectUseCase
from ...domain import ScanResult
from ..errors import InvalidScanPathError
from .schemas import (
    DetectionResponseSchema,
    DetectionStatsSchema,
    RawNodeSchema,
    RawLinkSchema
)


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionController:
    """
    Driving Port: Facade for the Detection Bounded Context.
    Exposes physical scanning capabilities to other contexts or the CLI.
    """

    scan_use_case: ScanProjectUseCase
    config: ConfigVo

    def scan_physical_project(
        self,
        target_path: Path | None = None,
        dirs_only: bool = False,
        scan_all: bool = False,
        import_depth: int = 0,
        focus_path: Path | None = None,
        include_paths: List[Path] | None = None,
    ) -> DetectionResponseSchema:
        """
        Executes the detection pipeline and returns a schema.
        Args:
            include_paths: Explicit list of physical paths to whitelist.
        """
        project_source_root = self.config.project.absolute_source_path
        
        # If no explicit focus provided, use target_path, else root
        actual_focus = focus_path if focus_path else (target_path if target_path else project_source_root)

        if not actual_focus.exists():
             # Updated: Raise standard Port Error instead of builtin FileNotFoundError
             raise InvalidScanPathError(str(actual_focus))

        # 1. Execute Application Logic (Pure Domain Output)
        result: ScanResult = self.scan_use_case.execute(
            scan_root=project_source_root,
            focus_path=actual_focus,
            dirs_only=dirs_only,
            scan_all=scan_all,
            import_depth=import_depth,
            include_paths=include_paths,
        )

        # 2. Map Domain Entities -> Transfer Schemas
        return self._map_to_schema(result)

    def _map_to_schema(self, domain_result: ScanResult) -> DetectionResponseSchema:
        """
        Private Mapper: Converts Domain ScanResult to Public DetectionResponseSchema.
        """
        graph_nodes: Dict[str, RawNodeSchema] = {}
        
        # Map Graph
        for node in domain_result.graph.all_nodes:
            links = [
                RawLinkSchema(
                    source=link.source_module,
                    target=link.target_module,
                    imported_symbols=link.imported_symbols
                )
                for link in node.imports
            ]
            
            graph_nodes[node.module_path] = RawNodeSchema(
                module_path=node.module_path,
                is_visible=node.is_visible,
                imports=links
            )

        # Map Stats
        stats = DetectionStatsSchema(
            total_files=domain_result.stats.total_files,
            total_modules=domain_result.stats.total_modules,
            total_relations=domain_result.stats.total_relations,
        )

        return DetectionResponseSchema(
            graph_nodes=graph_nodes,
            source_tree=domain_result.source_tree,
            stats=stats
        )