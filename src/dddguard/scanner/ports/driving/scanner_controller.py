from dataclasses import dataclass
from pathlib import Path
from typing import List

from dddguard.shared import ConfigVo

from ...app import RunScanUseCase, InspectTreeUseCase
from ...domain.value_objects import ScanReportVo, ClassifiedTreeVo
from .response_schema import ScanResponseSchema, ClassifiedNodeSchema


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerController:
    """
    Driving Port: Main Entrypoint for the Scanner System (Macro Context).
    Responsible for mapping Domain Results to Public Schemas.
    """

    run_scan_use_case: RunScanUseCase
    inspect_tree_use_case: InspectTreeUseCase
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
        Executes the full pipeline: Detection -> Classification -> Result.
        Maps logical filters (Context Names) to Physical Paths before calling the Use Case.
        """
        
        # Resolve Context Names -> Physical Paths
        include_paths: List[Path] | None = None
        if whitelist_contexts:
            include_paths = self._resolve_context_paths(whitelist_contexts)

        report: ScanReportVo = self.run_scan_use_case.execute(
            target_path=target_path,
            focus_path=target_path,
            dirs_only=dirs_only,
            scan_all=scan_all,
            import_depth=import_depth,
            include_paths=include_paths,
            whitelist_layers=whitelist_layers,  # <--- FIXED: Now passing the filter
        )
        
        return self._map_report_to_schema(report)

    def classify_tree(self, target_path: Path | None = None) -> ClassifiedNodeSchema:
        """
        Visualizes the directory tree with architectural tags.
        """
        path = target_path if target_path else self.config.project.absolute_source_path
        exclude = self.config.scanner.exclude_dirs
        
        tree_vo = self.inspect_tree_use_case.execute(path, exclude)
        return self._map_tree_to_schema(tree_vo)

    def _resolve_context_paths(self, context_names: List[str]) -> List[Path]:
        """
        Helper: Converts a list of Bounded Context names into absolute physical paths.
        Uses the ConfigVo to determine Macro Zones and Source Root.
        """
        root = self.config.project.absolute_source_path
        macro_map = self.config.project.macro_contexts # {zone: folder}
        
        # Pre-calculate Macro Paths
        # zone_paths = {"scanner": Path("/src/scanner")}
        zone_paths = {
            zone: (root / folder) 
            for zone, folder in macro_map.items()
        }
        
        resolved_paths = []
        
        for ctx_name in context_names:
            found = False
            
            # 1. Check if it matches a Macro Zone (Orchestrator Selection)
            # If user selected [macro: scanner] scanner (or just 'scanner'), they get the whole folder.
            if ctx_name in zone_paths:
                resolved_paths.append(zone_paths[ctx_name])
                found = True
            
            # 2. Check if it is a sub-context inside a Macro Zone
            if not found:
                for zone_path in zone_paths.values():
                    candidate = zone_path / ctx_name
                    if candidate.exists() and candidate.is_dir():
                        resolved_paths.append(candidate)
                        found = True
                        break
            
            # 3. Check if it is a general context in Root
            if not found:
                candidate = root / ctx_name
                if candidate.exists() and candidate.is_dir():
                    resolved_paths.append(candidate)
                    found = True
            
            # If not found, we ignore it (silent fail or log warning)
        
        return resolved_paths

    def _map_report_to_schema(self, report: ScanReportVo) -> ScanResponseSchema:
        return ScanResponseSchema(
            source_tree=report.source_tree,
            dependency_graph=report.dependency_graph,
            context_count=report.context_count,
            file_count=report.file_count,
            snapshot_file_count=report.snapshot_file_count,
            unclassified_count=report.unclassified_count,
            total_lines_of_code=report.total_lines_of_code,
            success=report.success,
            error_message=report.error_message
        )

    def _map_tree_to_schema(self, vo: ClassifiedTreeVo) -> ClassifiedNodeSchema:
        return ClassifiedNodeSchema(
            name=vo.name,
            is_dir=vo.is_dir,
            path_display=vo.path_display,
            passport=vo.passport,
            children=[self._map_tree_to_schema(c) for c in vo.children]
        )