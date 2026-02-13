import re
from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import (
    LayerEnum,
    ScopeEnum,
)

from .....shared.domain.registry import (
    DDD_LAYER_REGISTRY,
    DDD_SCOPE_REGISTRY,
    DDD_STRUCTURAL_REGISTRY,
)
from ..value_objects import ContextBoundaryVo


@dataclass(frozen=True, kw_only=True, slots=True)
class Stage0ContextDiscoveryService:
    """
    Domain Service: Stage 0 - Context Boundary Detection.

    Implements the "Stop-at-Layer" algorithm to determine the architectural boundary
    (Context, Macro Zone, and Scope) of a given file path.

    Strategy Priority:
    1.  **Directory Layer Match:** Searches for standard layer names (domain, app, ports)
        in the directory path. The first match defines the boundary.
    2.  **Filename Inference:** If no directory layer is found, checks if the filename
        itself implies a layer (e.g., `facade.py` -> PORTS).
    3.  **Generic Fallback:** Assumes the top-level folder is the Context name.
    """

    @staticmethod
    def detect_context_boundary(
        source_dir: str, relative_path_parts: tuple[str, ...]
    ) -> ContextBoundaryVo:
        """
        Executes the discovery logic.

        :param source_dir: The project source root (e.g., "src"). Used to strip technical prefixes.
        :param relative_path_parts: The file path split into parts.
        :return: A Value Object containing the discovered boundary and effective path parts.
        """
        # 1. Clean Path (Remove source_dir prefix if present to normalize analysis)
        analysis_parts = relative_path_parts
        source_dir_parts = tuple(p for p in Path(source_dir).parts if p and p != "/")

        if (
            source_dir_parts
            and len(analysis_parts) >= len(source_dir_parts)
            and analysis_parts[: len(source_dir_parts)] == source_dir_parts
        ):
            analysis_parts = analysis_parts[len(source_dir_parts) :]

        # 2. Strategy A: Directory "Stop-at-Layer"
        # Iterate to find the first directory that matches a known DDD Layer.
        for i, token in enumerate(analysis_parts):
            layer = Stage0ContextDiscoveryService._match_layer_token(token)

            if layer != LayerEnum.UNDEFINED:
                return Stage0ContextDiscoveryService._build_boundary(
                    analysis_parts, index=i, layer=layer
                )

        # 3. Strategy B: Filename Inference
        # If no directory layer found, check if the file itself indicates the layer.
        if analysis_parts:
            filename = analysis_parts[-1]
            file_layer = Stage0ContextDiscoveryService._infer_layer_from_filename(filename)

            if file_layer != LayerEnum.UNDEFINED:
                # Treat the file itself as the start of the layer.
                # Context = path before this file
                file_index = len(analysis_parts) - 1
                return Stage0ContextDiscoveryService._build_boundary(
                    analysis_parts, index=file_index, layer=file_layer
                )

        # 4. Strategy C: Generic Fallback
        # No layer detected. Assume standard Context Scope unless markers indicate otherwise.
        fallback_scope = ScopeEnum.CONTEXT
        fallback_context = None

        if analysis_parts:
            top_folder = analysis_parts[0]
            # Default assumption: The top folder IS the context name
            fallback_context = top_folder

            # Refine Scope based on architectural naming conventions
            if Stage0ContextDiscoveryService._match_scope_token(top_folder, ScopeEnum.SHARED):
                fallback_scope = ScopeEnum.SHARED
            elif Stage0ContextDiscoveryService._match_scope_token(top_folder, ScopeEnum.ROOT):
                fallback_scope = ScopeEnum.ROOT

        return ContextBoundaryVo(
            scope=fallback_scope,
            macro_path=None,
            context_name=fallback_context,
            effective_parts=analysis_parts,
            detected_layer_token=LayerEnum.UNDEFINED,
        )

    @staticmethod
    def _build_boundary(parts: tuple[str, ...], index: int, layer: LayerEnum) -> ContextBoundaryVo:
        """
        Constructs the boundary VO once a layer cutoff point is identified.
        Splits the path into [Macro/Context] and [Effective Internal Path].
        """
        context_idx = index - 1

        # Case: Layer is found at the root level (e.g. src/domain/...)
        if context_idx < 0:
            return ContextBoundaryVo(
                scope=ScopeEnum.ROOT,
                macro_path=None,
                context_name="root",
                effective_parts=parts[index:],
                detected_layer_token=layer,
            )

        context_name = parts[context_idx]

        # Determine Scope based on the identified context name
        scope = ScopeEnum.CONTEXT
        if Stage0ContextDiscoveryService._match_scope_token(context_name, ScopeEnum.SHARED):
            scope = ScopeEnum.SHARED
        elif Stage0ContextDiscoveryService._match_scope_token(context_name, ScopeEnum.ROOT):
            scope = ScopeEnum.ROOT

        # Macro Path is everything preceding the context folder
        macro_parts = parts[:context_idx]
        macro_path = "/".join(macro_parts) if macro_parts else None

        return ContextBoundaryVo(
            scope=scope,
            macro_path=macro_path,
            context_name=context_name,
            effective_parts=parts[index:],
            detected_layer_token=layer,
        )

    @staticmethod
    def _match_layer_token(token: str) -> LayerEnum:
        """Matches a directory string against the DDD Layer Registry."""
        for layer, regexes in DDD_LAYER_REGISTRY.items():
            if any(re.fullmatch(rx, token, re.IGNORECASE) for rx in regexes):
                return layer
        return LayerEnum.UNDEFINED

    @staticmethod
    def _match_scope_token(token: str, target_scope: ScopeEnum) -> bool:
        """Checks if a token matches a specific Scope pattern (e.g., 'shared')."""
        regexes = DDD_SCOPE_REGISTRY.get(target_scope, [])
        return any(re.fullmatch(rx, token, re.IGNORECASE) for rx in regexes)

    @staticmethod
    def _infer_layer_from_filename(filename: str) -> LayerEnum:
        """
        Reverse lookup: Checks if the filename matches any structural rule
        for a specific layer.

        Prioritizes layers that often contain root-level files (Composition, Ports, Adapters)
        to avoid false positives.
        """
        priority_check = [
            LayerEnum.COMPOSITION,
            LayerEnum.PORTS,
            LayerEnum.ADAPTERS,
            LayerEnum.GLOBAL,
        ]

        for layer in priority_check:
            layer_data = DDD_STRUCTURAL_REGISTRY.get(layer, {})
            # Check rules for all directions
            for direction_data in layer_data.values():
                for _comp_type, regexes in direction_data.items():
                    if any(re.fullmatch(rx, filename, re.IGNORECASE) for rx in regexes):
                        return layer

        return LayerEnum.UNDEFINED
