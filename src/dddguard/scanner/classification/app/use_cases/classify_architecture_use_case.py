from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from dddguard.shared.domain import (
ArchetypeType, ComponentPassport,   ScopeEnum, LayerEnum, DirectionEnum, MatchMethod
)

from ...domain import (
    EnrichedGraph, 
    EnrichedNodeVo, 
    ClassificationStatsVo,
    SrmEngineService
)

@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifyArchitectureUseCase:
    """
    App Service:
    Orchestrates the transformation from Physical Graph -> Architectural Graph.
    """

    srm_engine: SrmEngineService

    def execute(
        self, 
        raw_nodes: Dict[str, Any], # Map[module_path, {is_visible, imports...}]
        project_root: Path
    ) -> EnrichedGraph:
        
        enriched_nodes: Dict[str, EnrichedNodeVo] = {}
        
        total = 0
        classified = 0
        unknown = 0

        for module_path, node_data in raw_nodes.items():
            # Skip invisible nodes if they came through
            if not node_data.get("is_visible", True):
                continue

            total += 1
            
            # 1. Prepare Path for Analysis
            # module_path is "a.b.c". We need file stem and parts.
            parts = tuple(module_path.split("."))
            filename_stem = parts[-1] if parts else ""
            
            # 2. Identify
            passport = self.srm_engine.identify(
                relative_path_parts=parts, 
                filename_stem=filename_stem
            )

            # 3. Stats
            if passport.component_type == ArchetypeType.UNKNOWN:
                unknown += 1
            else:
                classified += 1

            # 4. Enrich
            # Extract raw import strings
            raw_imports = [
                link["target"] for link in node_data.get("imports", [])
            ]

            enriched_nodes[module_path] = EnrichedNodeVo(
                module_path=module_path,
                passport=passport,
                imports=raw_imports
            )

        stats = ClassificationStatsVo(
            total_nodes=total,
            classified_nodes=classified,
            unknown_nodes=unknown
        )

        return EnrichedGraph(nodes=enriched_nodes, stats=stats)

    def identify_single(self, file_path: Path, project_root: Path) -> ComponentPassport:
        """
        Identifies a single file or directory on the fly.
        """
        try:
            # Calculate relative path parts
            # e.g. /abs/src/ctx/layer/file.py -> ("src", "ctx", "layer", "file")
            # If file is not in project root, we might fail or return unknown
            if not file_path.is_absolute():
                file_path = file_path.resolve()
            
            # Handle case where file is outside project root
            if not str(file_path).startswith(str(project_root)):
                 return self._make_unknown(file_path)

            rel_path = file_path.relative_to(project_root)
            
            # Prepare parts
            parts = list(rel_path.parts)
            
            # Remove extension if it's a file
            if file_path.is_file():
                filename_stem = file_path.stem
                # Update last part to remove extension for the parts tuple
                parts[-1] = filename_stem
            else:
                filename_stem = file_path.name

            return self.srm_engine.identify(
                relative_path_parts=tuple(parts),
                filename_stem=filename_stem
            )
            
        except ValueError:
            return self._make_unknown(file_path)

    def _make_unknown(self, path: Path) -> ComponentPassport:
        """Helper to return empty passport"""
        return ComponentPassport(
            scope=ScopeEnum.CONTEXT, # Default fallback
            context_name=None,
            macro_zone=None,
            layer=LayerEnum.UNDEFINED,
            direction=DirectionEnum.UNDEFINED,
            component_type=ArchetypeType.UNKNOWN,
            match_method=MatchMethod.UNKNOWN
        )