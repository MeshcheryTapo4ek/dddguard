from dataclasses import dataclass
from pathlib import Path

from ...domain import SrmEngineService, ClassificationResultVo
from dddguard.shared import ScopeEnum


@dataclass(frozen=True, kw_only=True, slots=True)
class ClassifyFileUseCase:
    """
    App Service: Orchestrates the SRM v2.0 Identification Pipeline.
    """

    srm_engine: SrmEngineService

    def execute(self, file_path: Path, project_root: Path) -> ClassificationResultVo:
        try:
            rel_path = file_path.relative_to(project_root)
        except ValueError:
            return self._create_unknown(file_path.stem)

        parts = rel_path.parts
        if not parts:
            return self._create_unknown(file_path.stem)

        identity = self.srm_engine.identify(parts, file_path.stem)

        context_name = parts[0]
        if identity.scope == ScopeEnum.CONTEXT and len(parts) > 1:
            # Handle standard src/<context>/...
            context_name = parts[0]

        return ClassificationResultVo(
            scope=identity.scope,
            layer=identity.layer,
            component_type=identity.component_type,
            context_name=context_name,
            is_definitive=(str(identity.component_type) != "UNKNOWN"),
        )

    def _create_unknown(self, context_name: str) -> ClassificationResultVo:
        return ClassificationResultVo(
            scope=ScopeEnum.CONTEXT,
            layer="UNKNOWN",
            component_type="UNKNOWN",
            context_name=context_name,
            is_definitive=False,
        )
