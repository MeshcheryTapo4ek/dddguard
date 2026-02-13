import pytest

from dddguard.scanner.detection.domain import (
    ImportedModuleVo,
    RecursiveImportResolverService,
    ScannedModuleVo,
)


class TestRecursiveImportResolverService:
    @pytest.fixture
    def resolver(self):
        return RecursiveImportResolverService

    @pytest.fixture
    def registry(self) -> dict[str, ScannedModuleVo]:
        """
        Static registry for basic cases.
        """
        return {
            # Chain Depth 1: pkg -> pkg.internal
            "pkg": ScannedModuleVo(
                logical_path="pkg",
                file_path="pkg/__init__.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path="pkg.internal",
                        lineno=1,
                        is_relative=True,
                        imported_names=("A",),
                    )
                ],
            ),
            "pkg.internal": ScannedModuleVo(
                logical_path="pkg.internal",
                file_path="pkg/internal.py",
                content="",
                raw_imports=(),  # Defines A
            ),
            # Chain Depth 2: pkg.sub -> pkg.sub.deep -> pkg.core
            "pkg.sub": ScannedModuleVo(
                logical_path="pkg.sub",
                file_path="pkg/sub/__init__.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path="pkg.sub.deep",
                        lineno=1,
                        is_relative=True,
                        imported_names=("B",),
                    )
                ],
            ),
            "pkg.sub.deep": ScannedModuleVo(
                logical_path="pkg.sub.deep",
                file_path="pkg/sub/deep.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path="pkg.core",
                        lineno=1,
                        is_relative=False,
                        imported_names=("B",),
                    )
                ],
            ),
            "pkg.core": ScannedModuleVo(
                logical_path="pkg.core",
                file_path="pkg/core.py",
                content="",
                raw_imports=(),  # Defines B
            ),
            # Submodule Priority Case
            "utils": ScannedModuleVo(
                logical_path="utils",
                file_path="utils/__init__.py",
                content="",
                raw_imports=(),
            ),
            "utils.helper": ScannedModuleVo(
                logical_path="utils.helper",
                file_path="utils/helper.py",
                content="",
                raw_imports=(),
            ),
        }

    def test_resolve_direct_definition(self, resolver, registry):
        """Depth 0: Symbol defined in place."""
        result = resolver.resolve(registry, "pkg.internal", "A", source_dir_name="src")
        assert result == "pkg.internal"

    def test_resolve_depth_1(self, resolver, registry):
        """Depth 1: One re-export jump."""
        result = resolver.resolve(registry, "pkg", "A", source_dir_name="src")
        assert result == "pkg.internal"

    def test_resolve_depth_2(self, resolver, registry):
        """Depth 2: Two re-export jumps."""
        result = resolver.resolve(registry, "pkg.sub", "B", source_dir_name="src")
        assert result == "pkg.core"

    @pytest.mark.parametrize("depth", [3, 4, 5, 10])
    def test_resolve_dynamic_depth(self, resolver, depth):
        """
        Stress Test: Generates a chain of arbitrary depth to ensure recursion works.
        Chain: start -> node_1 -> node_2 ... -> node_{depth} (Target)
        """
        registry = {}
        target_symbol = "Target"

        # 1. Create the Final Target Node (The Source of Truth)
        final_node_name = f"node_{depth}"
        registry[final_node_name] = ScannedModuleVo(
            logical_path=final_node_name,
            file_path=f"{final_node_name}.py",
            content="",
            raw_imports=(),  # It defines the symbol locally
        )

        # 2. Build the Chain backwards
        for i in range(depth):
            current_name = f"node_{i}" if i > 0 else "start"
            next_name = f"node_{i + 1}"

            registry[current_name] = ScannedModuleVo(
                logical_path=current_name,
                file_path=f"{current_name}.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path=next_name,
                        lineno=1,
                        is_relative=False,
                        imported_names=(target_symbol,),
                    )
                ],
            )

        # Act
        result = resolver.resolve(registry, "start", target_symbol, source_dir_name="src")

        # Assert
        assert result == final_node_name

    def test_resolve_submodule_priority(self, resolver, registry):
        """Check that physical submodule presence beats imports."""
        result = resolver.resolve(registry, "utils", "helper", source_dir_name="src")
        assert result == "utils.helper"

    def test_resolve_cycle_protection(self, resolver):
        """Case: A imports X from B, B imports X from A. Should prevent infinite recursion."""
        registry = {
            "A": ScannedModuleVo(
                logical_path="A",
                file_path="A.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path="B",
                        lineno=1,
                        is_relative=False,
                        imported_names=("X",),
                    )
                ],
            ),
            "B": ScannedModuleVo(
                logical_path="B",
                file_path="B.py",
                content="",
                raw_imports=[
                    ImportedModuleVo(
                        module_path="A",
                        lineno=1,
                        is_relative=False,
                        imported_names=("X",),
                    )
                ],
            ),
        }
        result = resolver.resolve(registry, "A", "X", source_dir_name="src")
        assert result in ["A", "B"]

    def test_resolve_from_root_context(self, resolver):
        """
        Case: 'from .. import utils' where '..' resolves to project root.
        The start_module_path passed to resolve is "" (empty string).
        The resolver must handle this gracefully and look for 'utils' at the top level.
        """
        registry = {
            "utils": ScannedModuleVo(
                logical_path="utils", file_path="utils.py", content="", raw_imports=()
            )
        }

        # Act: start_path="" simulates import from root
        result = resolver.resolve(
            registry, start_module_path="", imported_name="utils", source_dir_name="src"
        )

        # Assert
        assert result == "utils"
