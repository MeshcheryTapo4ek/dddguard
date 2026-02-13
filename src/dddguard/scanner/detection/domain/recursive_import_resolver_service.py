from dataclasses import dataclass

from .value_objects import ScannedModuleVo


@dataclass(frozen=True, slots=True)
class RecursiveImportResolverService:
    """
    Domain Service: Resolves the ultimate source of an imported name.
    It traverses the chain of re-exports (typically found in __init__.py files)
    to identify the physical module where a symbol is actually defined.
    """

    @staticmethod
    def resolve(
        registry: dict[str, ScannedModuleVo],
        start_module_path: str,
        imported_name: str,
        source_dir_name: str,
    ) -> str:
        """
        Recursively traces the source of an imported symbol starting from a specific module.

        :param registry: The complete map of scanned modules.
        :param start_module_path: The module path where the import occurs (e.g. "pkg").
        :param imported_name: The specific symbol being imported (e.g. "Service" or "submodule").
        :param source_dir_name: The source root directory name, used for path normalization.
        :return: The logical path of the module that defines the symbol or is the submodule itself.
        """
        return RecursiveImportResolverService._resolve_recursive(
            registry, start_module_path, imported_name, source_dir_name, visited=set()
        )

    @staticmethod
    def _resolve_recursive(
        registry: dict[str, ScannedModuleVo],
        current_path: str,
        name: str,
        source_dir_name: str,
        visited: set[str],
    ) -> str:
        # 1. Normalize current path if necessary (e.g. strip root prefix)
        real_path = current_path
        if real_path not in registry:
            normalized = RecursiveImportResolverService._normalize_path(real_path, source_dir_name)
            # Use normalized only if exists in registry
            # or if the original path was effectively empty (root context)
            if normalized and normalized in registry:
                real_path = normalized

        # 2. Cycle Detection
        state_key = f"{real_path}::{name}"
        if state_key in visited:
            return real_path
        visited.add(state_key)

        # 3. Check for Submodule Existence
        # If the imported name corresponds to a physical file/module, that is the source.
        # FIX: Handle empty real_path (Root context)
        candidate_submodule = f"{real_path}.{name}" if real_path else name

        if candidate_submodule in registry:
            return candidate_submodule

        norm_sub = RecursiveImportResolverService._normalize_path(
            candidate_submodule, source_dir_name
        )
        if norm_sub and norm_sub in registry:
            return norm_sub

        # 4. Check Container Existence
        # If the current module itself is missing (e.g. external lib or empty root), stop here.
        if real_path not in registry and real_path != "":
            return real_path

        # If we are at root ("") and didn't find the submodule, we can't check 'raw_imports' of empty string.
        if real_path == "":
            return real_path

        module_vo = registry[real_path]

        # 5. Check for Re-exports
        # Look for explicit imports of the symbol in the current module.
        if module_vo.raw_imports:
            for imp in module_vo.raw_imports:
                if name in imp.imported_names:
                    target = imp.module_path
                    # Skip invalid/empty targets from parser edge cases
                    # Note: target might be "" if importing from root, that is valid here.

                    return RecursiveImportResolverService._resolve_recursive(
                        registry, target, name, source_dir_name, visited
                    )

        # 6. Fallback: Symbol Definition
        # If not a submodule and not imported, it must be defined locally in this module.
        return real_path

    @staticmethod
    def _normalize_path(path: str, source_dir_name: str) -> str | None:
        parts = path.split(".")
        if parts and parts[0] == source_dir_name:
            return ".".join(parts[1:])
        return None
