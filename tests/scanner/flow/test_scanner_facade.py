"""
Flow tests for ScannerFacade.

ScannerFacade is the top-level driving port of the Scanner context.
It owns the ConfigVo and delegates to three use cases:
  - RunScanUseCase          (scan_project)
  - InspectTreeUseCase      (classify_tree)
  - DiscoverContextsUseCase (discover_contexts)
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dddguard.scanner.ports.errors import InvalidScanPathError
from dddguard.scanner.domain.value_objects import DiscoveredContextVo
from dddguard.scanner.ports.driving.scanner_facade import (
    ContextListSchema,
    ScannerFacade,
)
from dddguard.shared.domain import (
    CodeGraph,
    ConfigVo,
    ProjectConfig,
    ScannerConfig,
)
from tests.scanner.conftest import make_classified_graph

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def source_dir(tmp_path) -> Path:
    d = tmp_path / "src"
    d.mkdir()
    return d


@pytest.fixture
def config(source_dir) -> ConfigVo:
    return ConfigVo(
        project=ProjectConfig(
            source_dir="src",
            project_root=source_dir.parent,
        ),
        scanner=ScannerConfig(),
    )


@pytest.fixture
def run_scan_uc():
    return MagicMock()


@pytest.fixture
def inspect_tree_uc():
    return MagicMock()


@pytest.fixture
def discover_contexts_uc():
    return MagicMock()


@pytest.fixture
def facade(run_scan_uc, inspect_tree_uc, discover_contexts_uc, config) -> ScannerFacade:
    return ScannerFacade(
        run_scan_use_case=run_scan_uc,
        inspect_tree_use_case=inspect_tree_uc,
        discover_contexts_use_case=discover_contexts_uc,
        config=config,
    )


# ---------------------------------------------------------------------------
# scan_project()
# ---------------------------------------------------------------------------


class TestScannerFacadeScanProject:
    def test_with_explicit_target_path(self, facade, run_scan_uc, source_dir, config):
        """When target_path is given, it should be used directly."""
        expected = CodeGraph()
        run_scan_uc.return_value = expected

        result = facade.scan_project(target_path=source_dir)

        assert result is expected
        run_scan_uc.assert_called_once_with(
            scanner_config=config.scanner,
            source_dir=source_dir,
            scan_all=False,
            import_depth=0,
            whitelist_layers=None,
            whitelist_contexts=None,
            include_assets=True,
        )

    def test_with_target_path_none_uses_config(self, facade, run_scan_uc, source_dir, config):
        """When target_path=None, the facade resolves from config."""
        run_scan_uc.return_value = CodeGraph()

        facade.scan_project(target_path=None)

        call_kwargs = run_scan_uc.call_args.kwargs
        # Should resolve to the same directory
        assert call_kwargs["source_dir"].resolve() == source_dir.resolve()


# ---------------------------------------------------------------------------
# classify_tree()
# ---------------------------------------------------------------------------


class TestScannerFacadeClassifyTree:
    def test_delegates_to_inspect_tree_uc(self, facade, inspect_tree_uc, source_dir, config):
        expected = make_classified_graph([{"path": "a.b"}])
        inspect_tree_uc.return_value = expected

        result = facade.classify_tree(target_path=source_dir)

        assert result is expected
        inspect_tree_uc.assert_called_once_with(
            scanner_config=config.scanner,
            source_dir=source_dir,
            scan_all=False,
        )


# ---------------------------------------------------------------------------
# discover_contexts()
# ---------------------------------------------------------------------------


class TestScannerFacadeDiscoverContexts:
    def test_returns_context_list_schema(self, facade, discover_contexts_uc, source_dir, config):
        discover_contexts_uc.return_value = [
            DiscoveredContextVo(context_name="billing", macro_zone=None),
            DiscoveredContextVo(context_name="shared", macro_zone=None),
        ]

        result = facade.discover_contexts(target_path=source_dir)

        assert isinstance(result, ContextListSchema)
        assert len(result.contexts) == 2
        assert result.contexts[0].context_name == "billing"
        assert result.contexts[1].context_name == "shared"

        discover_contexts_uc.assert_called_once_with(
            scanner_config=config.scanner,
            source_dir=source_dir,
            scan_all=False,
        )


# ---------------------------------------------------------------------------
# _get_source_dir() via public methods
# ---------------------------------------------------------------------------


class TestScannerFacadeGetSourceDir:
    def test_raises_when_source_dir_not_configured(self, run_scan_uc):
        """If project config has no source_dir, InvalidScanPathError is raised."""
        config = ConfigVo(
            project=ProjectConfig(source_dir=None, project_root=None),
        )
        facade = ScannerFacade(
            run_scan_use_case=run_scan_uc,
            inspect_tree_use_case=MagicMock(),
            discover_contexts_use_case=MagicMock(),
            config=config,
        )

        with pytest.raises(InvalidScanPathError, match="No 'source_dir'"):
            facade.scan_project()

    def test_raises_when_path_does_not_exist(self, run_scan_uc, tmp_path):
        """If the resolved path doesn't exist on disk, InvalidScanPathError is raised."""
        config = ConfigVo(
            project=ProjectConfig(
                source_dir="nonexistent_dir",
                project_root=tmp_path,
            ),
        )
        facade = ScannerFacade(
            run_scan_use_case=run_scan_uc,
            inspect_tree_use_case=MagicMock(),
            discover_contexts_use_case=MagicMock(),
            config=config,
        )

        with pytest.raises(InvalidScanPathError, match="does not exist"):
            facade.scan_project()

    def test_raises_when_path_is_file(self, run_scan_uc, tmp_path):
        """If the resolved path is a file (not a dir), InvalidScanPathError is raised."""
        file_path = tmp_path / "src"
        file_path.write_text("not a directory")

        config = ConfigVo(
            project=ProjectConfig(
                source_dir="src",
                project_root=tmp_path,
            ),
        )
        facade = ScannerFacade(
            run_scan_use_case=run_scan_uc,
            inspect_tree_use_case=MagicMock(),
            discover_contexts_use_case=MagicMock(),
            config=config,
        )

        with pytest.raises(InvalidScanPathError, match="not a directory"):
            facade.scan_project()

    def test_valid_path_returns_resolved(self, facade, run_scan_uc, source_dir):
        """A properly configured path should resolve and work."""
        run_scan_uc.return_value = CodeGraph()
        # This should not raise
        facade.scan_project()
        assert run_scan_uc.called
