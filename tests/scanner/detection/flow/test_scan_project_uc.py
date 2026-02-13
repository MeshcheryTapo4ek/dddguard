from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, create_autospec

import pytest

from dddguard.scanner.detection.app.interfaces import IProjectReader
from dddguard.scanner.detection.app.scan_project_uc import ScanProjectUseCase
from dddguard.scanner.detection.domain import SourceFileVo
from dddguard.shared.domain import CodeGraph, NodeStatus, ScannerConfig


class TestScanProjectUseCaseFlow:
    """
    FLOW Test: Verifies the orchestration inside ScanProjectUseCase.
    Mocks the Driven Port (IProjectReader) but uses real Domain Services
    (AstImportParser, RecursiveResolver) implicitly.
    """

    @pytest.fixture
    def mock_reader(self) -> MagicMock:
        return create_autospec(IProjectReader, instance=True)

    @pytest.fixture
    def use_case(self, mock_reader) -> ScanProjectUseCase:
        return ScanProjectUseCase(project_reader=mock_reader)

    def test_build_graph_linking_logic(self, use_case: ScanProjectUseCase, mock_reader: MagicMock):
        """
        Scenario: A project with nested structure and various import types.
        Goal: Verify that _build_graph correctly links nodes based on parsed imports,
              including correct resolution of 'from . import submodule'.

        Structure:
        /root/
          main.py          -> imports 'utils', 'libs.external'
          utils.py         -> (no imports)
          pkg/
            __init__.py    -> from . import service
            service.py     -> from .. import utils
        """
        scan_root = Path("/root")

        # Prepare Virtual Files
        files_data = [
            # 1. src.main
            SourceFileVo(
                path=scan_root / "main.py",
                content=dedent("""
                    import utils
                    import sqlalchemy  # External (should not link)
                """),
            ),
            # 2. src.utils
            SourceFileVo(path=scan_root / "utils.py", content=""),
            # 3. src.pkg (__init__)
            SourceFileVo(path=scan_root / "pkg/__init__.py", content="from . import service"),
            # 4. src.pkg.service
            SourceFileVo(path=scan_root / "pkg/service.py", content="from .. import utils"),
        ]

        # Setup Mock
        mock_reader.read_project.return_value = iter(files_data)

        # Act
        graph: CodeGraph = use_case(scanner_config=ScannerConfig(), target_path=scan_root)

        # Assertions

        # 1. Check Nodes Existence
        assert "main" in graph.nodes
        assert "utils" in graph.nodes
        assert "pkg" in graph.nodes
        assert "pkg.service" in graph.nodes

        # 2. Check Linking: main -> utils
        main_node = graph.get_node("main")
        assert main_node.status == NodeStatus.LINKED
        assert "utils" in main_node.imports
        # External lib 'sqlalchemy' should NOT be linked because it's not in registry
        assert "sqlalchemy" not in main_node.imports

        # 3. Check Linking: pkg (__init__) -> pkg.service
        # This was previously failing. Now RecursiveResolver should identify 'service' as a module.
        pkg_node = graph.get_node("pkg")
        assert "pkg.service" in pkg_node.imports, "Package init should link to its submodule"

        # 4. Check Linking: pkg.service -> utils (Deep Relative Resolution)
        service_node = graph.get_node("pkg.service")
        # 'from .. import utils' -> resolves to 'utils'
        assert "utils" in service_node.imports

    def test_build_graph_root_prefix_normalization(
        self, use_case: ScanProjectUseCase, mock_reader: MagicMock
    ):
        """
        Scenario: Imports include the root directory name.
        Graph Builder should strip it to find the internal module.

        Root: /app
        File: /app/main.py
        Code: import app.core
        Target File: /app/core.py (Logical: 'core')
        """
        scan_root = Path("/app")

        files_data = [
            SourceFileVo(path=scan_root / "main.py", content="import app.core"),
            SourceFileVo(path=scan_root / "core.py", content=""),
        ]
        mock_reader.read_project.return_value = iter(files_data)

        # Act
        graph = use_case(scanner_config=ScannerConfig(), target_path=scan_root)

        # Assert
        main_node = graph.get_node("main")

        # 'app.core' normalized to 'core'
        assert "core" in main_node.imports
