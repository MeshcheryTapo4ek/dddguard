from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from dddguard.shared.domain import ComponentPassport, ConfigVo

from ...app import ClassifyArchitectureUseCase
from ...domain import EnrichedGraph
from .schemas import (
    ClassificationResponseSchema,
    ClassifiedNodeSchema
)


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassificationController:
    """
    Driving Port: Facade for the Classification Context.
    """

    use_case: ClassifyArchitectureUseCase
    config: ConfigVo

    def classify_graph(
        self, 
        raw_graph_nodes: Dict[str, Any] # Accepts dict from Detection Schema
    ) -> ClassificationResponseSchema:
        """
        Takes raw graph data and returns an architecturally classified graph.
        """
        project_root = self.config.project.absolute_source_path

        # 1. Execute Logic
        enriched_graph: EnrichedGraph = self.use_case.execute(
            raw_nodes=raw_graph_nodes,
            project_root=project_root
        )

        # 2. Map to Schema
        return self._map_to_schema(enriched_graph)

    def identify_component(self, file_path: Path) -> ComponentPassport:
        """
        Identifies a single physical component (file or dir) without graph context.
        """
        project_root = self.config.project.absolute_source_path
        
        return self.use_case.identify_single(
            file_path=file_path,
            project_root=project_root
        )

    def _map_to_schema(self, graph: EnrichedGraph) -> ClassificationResponseSchema:
        schema_nodes = {}
        for path, node in graph.nodes.items():
            schema_nodes[path] = ClassifiedNodeSchema(
                module_path=path,
                passport=node.passport,
                direct_dependencies=node.imports
            )

        return ClassificationResponseSchema(
            nodes=schema_nodes,
            coverage_percent=graph.stats.coverage_percent,
            total_components=graph.stats.total_nodes,
            unknown_components=graph.stats.unknown_nodes
        )