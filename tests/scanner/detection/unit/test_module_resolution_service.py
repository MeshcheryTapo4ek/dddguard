from pathlib import Path

import pytest

from dddguard.scanner.detection.domain.module_resolution_service import (
    ModuleResolutionService,
)


class TestModuleResolutionService:
    @pytest.fixture
    def service(self) -> ModuleResolutionService:
        return ModuleResolutionService()

    @pytest.mark.parametrize(
        ("root", "file_rel_path", "expected_logical"),
        [
            # 1. Standard Module
            ("src", "utils/helper.py", "utils.helper"),
            # 2. Deep Nesting
            ("src", "core/auth/jwt/handlers.py", "core.auth.jwt.handlers"),
            # 3. Root Module
            ("src", "main.py", "main"),
            # 4. Package (__init__)
            ("src", "users/__init__.py", "users"),
            # 5. Nested Package
            ("src", "api/v1/__init__.py", "api.v1"),
            # 6. Non-Python File (Asset) - suffix stripping
            ("src", "assets/logo.png", "assets.logo"),
            # 7. Complex extensions (takes only last suffix)
            ("src", "data/archive.tar.gz", "data.archive.tar"),
            # 8. Dots in folder names
            ("src", "my.library/module.py", "my.library.module"),
        ],
    )
    def test_calculate_logical_path_success(
        self,
        service: ModuleResolutionService,
        root: str,
        file_rel_path: str,
        expected_logical: str,
    ):
        """
        Verify correct transformation of physical paths to logical dot-notation.
        """
        # Arrange
        # We simulate absolute paths to match real behavior
        base = Path("/app") / root
        target_file = base / file_rel_path

        # Act
        result = service.calculate_logical_path(target_file, base)

        # Assert
        assert result == expected_logical

    def test_calculate_logical_path_outside_root_returns_none(
        self, service: ModuleResolutionService
    ):
        """
        Edge Case: File is physically outside the source root.
        Must return None (boundary protection).
        """
        # Arrange
        root = Path("/app/src")
        # File is in /app/libs, which is a sibling, not child of src
        outside_file = Path("/app/libs/external.py")

        # Act
        result = service.calculate_logical_path(outside_file, root)

        # Assert
        assert result is None

    def test_calculate_logical_path_root_init(self, service: ModuleResolutionService):
        """
        Edge Case: __init__.py directly in the source root.
        Should logically map to an empty string (representing the root package itself).
        """
        # Arrange
        root = Path("/app/src")
        target = root / "__init__.py"

        # Act
        result = service.calculate_logical_path(target, root)

        # Assert
        # "src/__init__.py" relative to "src" is "__init__.py"
        # suffix removed -> "__init__"
        # parts popped -> []
        # join -> ""
        assert result == ""
