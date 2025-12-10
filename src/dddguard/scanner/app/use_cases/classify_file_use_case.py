from dataclasses import dataclass
from pathlib import Path

from ...domain import (
    ScopeHeuristicService,
    LayerHeuristicService,
    RegexMatcherService,
    ClassificationResultVo,
)
from dddguard.shared import ContextLayerEnum, OtherTypeEnum, ProjectBoundedContextNames


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifyFileUseCase:
    """
    App Service: Orchestrates the identification pipeline (Scope -> Layer -> Regex).
    """
    scope_service: ScopeHeuristicService
    layer_service: LayerHeuristicService
    regex_service: RegexMatcherService

    def execute(self, file_path: Path, project_root: Path) -> ClassificationResultVo:
        try:
            rel_path = file_path.relative_to(project_root)
        except ValueError:
            return self._create_unknown(file_path.stem)

        parts = rel_path.parts
        if not parts:
            return self._create_unknown(file_path.stem)

        # Prepare path parts for analysis
        clean_parts_list = list(parts)
        clean_parts_list[-1] = file_path.stem
        analysis_parts = tuple(clean_parts_list)

        # 1. Determine Scope & Context Name
        scope = self.scope_service.determine_scope(analysis_parts[0])
        context_name, internal_parts = self._resolve_context_context(scope, analysis_parts)

        # 2. Heuristic Layer Analysis
        guessed_layer, strong_type = self.layer_service.analyze(internal_parts)

        if strong_type:
            return ClassificationResultVo(
                scope=scope,
                layer=guessed_layer,
                component_type=strong_type,
                context_name=context_name,
                is_definitive=True,
            )

        # 3. Regex Refinement
        matched_rule = self.regex_service.match(
            scope=scope,
            path_parts=internal_parts,
            filename=file_path.stem,
            layer_hint=guessed_layer,
        )

        if matched_rule:
            return ClassificationResultVo(
                scope=scope,
                layer=matched_rule.layer,
                component_type=matched_rule.component_type,
                context_name=context_name,
                is_definitive=True,
            )

        if guessed_layer:
            return ClassificationResultVo(
                scope=scope,
                layer=guessed_layer,
                component_type=OtherTypeEnum.OTHER,
                context_name=context_name,
                is_definitive=False,
            )

        return self._create_unknown(context_name)

    def _resolve_context_context(self, scope: ProjectBoundedContextNames, parts: tuple) -> tuple[str, tuple]:
        """Helper to extract clean context name and internal path parts."""
        context_name = parts[0]
        internal_parts = parts

        if scope == ProjectBoundedContextNames.CONTEXT and "contexts" in parts:
            idx = parts.index("contexts")
            if idx + 1 < len(parts):
                context_name = parts[idx + 1]
                internal_parts = parts[idx + 1 :]
        
        elif scope == ProjectBoundedContextNames.SHARED:
            context_name = "shared"
            if parts[0] == "shared":
                internal_parts = parts[1:]

        return context_name, internal_parts

    def _create_unknown(self, context_name: str) -> ClassificationResultVo:
        return ClassificationResultVo(
            scope=ProjectBoundedContextNames.CONTEXT,
            layer=ContextLayerEnum.OTHER,
            component_type=OtherTypeEnum.OTHER,
            context_name=context_name,
            is_definitive=False,
        )