from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List

from dddguard.shared.domain import ComponentPassport
from ....app import IDetectionGateway, IClassificationGateway
from ....domain.value_objects import DetectionResultVo, ClassificationResultVo
from ....detection.ports.driving import DetectionController
from ....classification.ports.driving import ClassificationController
from ....classification.domain import EnrichedNodeVo 

from ...errors import GatewayIntegrationError


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionInternalGateway(IDetectionGateway):
    """
    Adapter: Wraps the DetectionController.
    Maps DetectionResponseSchema -> DetectionResultVo.
    """
    controller: DetectionController

    def scan(
        self,
        target_path: Path | None,
        dirs_only: bool,
        scan_all: bool,
        import_depth: int,
        focus_path: Path | None,
        include_paths: List[Path] | None,
    ) -> DetectionResultVo:
        try:
            schema = self.controller.scan_physical_project(
                target_path=target_path,
                dirs_only=dirs_only,
                scan_all=scan_all,
                import_depth=import_depth,
                focus_path=focus_path,
                include_paths=include_paths
            )
            
            # For graph_nodes, we pass the raw dict structure required by Classification
            raw_nodes = {k: asdict(v) for k, v in schema.graph_nodes.items()}
            
            return DetectionResultVo(
                graph_nodes=raw_nodes,
                source_tree=schema.source_tree,
                stats={
                    "total_files": schema.stats.total_files,
                    "total_modules": schema.stats.total_modules,
                    "total_relations": schema.stats.total_relations
                }
            )
        except Exception as e:
            raise GatewayIntegrationError("DetectionGateway", e) from e


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationInternalGateway(IClassificationGateway):
    """
    Adapter: Wraps the ClassificationController.
    Maps ClassificationResponseSchema -> ClassificationResultVo.
    """
    controller: ClassificationController

    def classify(self, raw_graph_nodes: Dict[str, Any]) -> ClassificationResultVo:
        try:
            schema = self.controller.classify_graph(raw_graph_nodes=raw_graph_nodes)
            
            # --- STRICT MAPPING (Schema DTO -> Domain VO) ---
            # We map explicit fields instead of using asdict/dicts
            mapped_nodes: Dict[str, EnrichedNodeVo] = {}
            
            for path, node_schema in schema.nodes.items():
                mapped_nodes[path] = EnrichedNodeVo(
                    module_path=node_schema.module_path,
                    passport=node_schema.passport, # Passport is shared, safe to pass
                    imports=node_schema.direct_dependencies # Map schema field to VO field
                )

            return ClassificationResultVo(
                nodes=mapped_nodes,
                unknown_count=schema.unknown_components
            )
        except Exception as e:
            raise GatewayIntegrationError("ClassificationGateway", e) from e

    def identify_component(self, file_path: Path) -> ComponentPassport:
        try:
            return self.controller.identify_component(file_path=file_path)
        except Exception as e:
            raise GatewayIntegrationError("ClassificationGateway.Identify", e) from e