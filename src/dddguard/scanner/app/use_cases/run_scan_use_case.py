from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Set

from ..interfaces import IDetectionGateway, IClassificationGateway
from ...domain.value_objects import ScanReportVo
from ...classification.domain import EnrichedNodeVo # Strict Type Import


@dataclass(frozen=True, kw_only=True, slots=True)
class RunScanUseCase:
    """
    Macro UseCase: Orchestrates the full scanning pipeline.
    """

    detection_gateway: IDetectionGateway
    classification_gateway: IClassificationGateway

    def execute(
        self,
        target_path: Path | None,
        focus_path: Path | None,
        dirs_only: bool = False,
        scan_all: bool = False,
        import_depth: int = 0,
        include_paths: List[Path] | None = None,
        whitelist_layers: List[str] | None = None,
    ) -> ScanReportVo:
        
        # 1. DETECT (Physical Layer)
        detection_result = self.detection_gateway.scan(
            target_path=target_path,
            dirs_only=dirs_only,
            scan_all=scan_all,
            import_depth=import_depth,
            focus_path=focus_path,
            include_paths=include_paths
        )

        # 2. CLASSIFY (Logical Layer)
        classification_result = self.classification_gateway.classify(
            raw_graph_nodes=detection_result.graph_nodes
        )
        
        final_nodes = classification_result.nodes
        
        # 3. APPLY LOGICAL FILTERS (Layers)
        if whitelist_layers:
            final_nodes = self._filter_by_layers(final_nodes, set(whitelist_layers))

        # 4. MERGE & FORMAT
        # We need to serialize the VO nodes back to dicts for the final Report/JSON output
        # or update ScanReportVo to accept VOs. For now, strict mapping to dict:
        
        # Helper to convert VO back to generic dict for the final Report (if needed by UI)
        # Assuming the UI expects simple dicts in dependency_graph.
        graph_export = {
            k: {
                "module_path": v.module_path,
                "passport": v.passport,
                "imports": v.imports
            } 
            for k, v in final_nodes.items()
        }

        return ScanReportVo(
            source_tree=detection_result.source_tree,
            dependency_graph=graph_export,
            
            context_count=0,
            file_count=detection_result.stats.get("total_files", 0),
            snapshot_file_count=len(final_nodes),
            unclassified_count=classification_result.unknown_count,
            total_lines_of_code=0,
            success=True
        )

    def _filter_by_layers(
        self, 
        nodes: Dict[str, EnrichedNodeVo], 
        allowed_layers: Set[str]
    ) -> Dict[str, EnrichedNodeVo]:
        """
        Filters the classification graph nodes based on the passport layer.
        Uses Strict Typing (EnrichedNodeVo).
        """
        filtered = {}
        for path, node in nodes.items():  
            if node.passport.layer.value in allowed_layers:
                filtered[path] = node
                
        return filtered