import logging
from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import (
    ArchetypeType,
    ComponentPassport,
    DirectionEnum,
    LayerEnum,
    MatchMethod,
    ScopeEnum,
)

from ..domain import (
    Stage0ContextDiscoveryService,
    Stage1CoordinateDefinitionService,
    Stage2RulePrioritizationService,
    Stage3_4ComponentMatchingService,
)

# Setup module-level logger
logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True, slots=True)
class IdentifyComponentUseCase:
    """
    App Service (Atomic Use Case): Single File Identification.

    Orchestrates the classification pipeline to determine the architectural role
    (Passport) of a specific file within the project structure.
    """

    def __call__(self, file_path: Path, source_dir: Path) -> ComponentPassport:
        """
        Executes the identification logic for a given file.
        """
        try:
            # 1. Path Normalization & Security Check
            abs_file_path = file_path.resolve()
            abs_source_dir = source_dir.resolve()

            # Ensure file is inside project
            rel_path = abs_file_path.relative_to(abs_source_dir)
            parts = list(rel_path.parts)

            # Prepare filename stem for analysis
            filename_stem = file_path.stem
            parts[-1] = filename_stem

            # --- EXECUTE PIPELINE ---

            # Stage 0: Context Boundary Detection
            boundary = Stage0ContextDiscoveryService.detect_context_boundary(
                source_dir=str(source_dir),
                relative_path_parts=tuple(parts),
            )

            # Stage 1: Coordinate Definition
            coords = Stage1CoordinateDefinitionService.define_coordinates(boundary)

            # --- INTERCEPT: AUTOMATIC MARKER CLASSIFICATION ---
            if filename_stem.startswith("__") and filename_stem.endswith("__"):
                return ComponentPassport(
                    scope=coords.scope,
                    context_name=boundary.context_name,
                    macro_zone=boundary.macro_path,
                    layer=coords.layer,
                    direction=coords.direction,
                    component_type=ArchetypeType.MARKER,
                    match_method=MatchMethod.NAME,
                )

            # Stage 2: Rule Prioritization
            pool = Stage2RulePrioritizationService.get_applicable_rules(
                coords.layer, coords.direction
            )

            # Stage 3 & 4: Matching
            comp_type, method, matched_layer = Stage3_4ComponentMatchingService.match_component(
                pool=pool,
                searchable_tokens=coords.searchable_tokens,
                filename_stem=filename_stem,
            )

            # --- POST-PROCESSING: LAYER INFERENCE ---
            final_layer = coords.layer
            if final_layer == LayerEnum.UNDEFINED and matched_layer != LayerEnum.UNDEFINED:
                final_layer = matched_layer

            # Construct Passport
            passport = ComponentPassport(
                scope=coords.scope,
                context_name=boundary.context_name,
                macro_zone=boundary.macro_path,
                layer=final_layer,
                direction=coords.direction,
                component_type=comp_type,
                match_method=method,
            )

            if passport.context_name == "src":
                logger.debug(
                    "Unexpected 'src' context — File: %s, Boundary: %s",
                    abs_file_path,
                    boundary,
                )

            return passport

        except ValueError:
            logger.warning(
                "Skipping file outside project root: %s (Root: %s)",
                file_path,
                source_dir,
            )
            return IdentifyComponentUseCase._make_unknown()
        except Exception as e:
            logger.error("Failed to identify component for %s: %s", file_path, e, exc_info=True)
            return IdentifyComponentUseCase._make_unknown()

    @staticmethod
    def _make_unknown() -> ComponentPassport:
        """Returns a default 'Unknown' passport for failed identifications."""
        return ComponentPassport(
            scope=ScopeEnum.CONTEXT,
            context_name=None,
            macro_zone=None,
            layer=LayerEnum.UNDEFINED,
            direction=DirectionEnum.UNDEFINED,
            component_type=ArchetypeType.UNKNOWN,
            match_method=MatchMethod.UNKNOWN,
        )
