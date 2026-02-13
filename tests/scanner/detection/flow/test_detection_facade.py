"""
Flow tests for DetectionFacade.

The facade validates the target path and delegates to the ScanProjectUseCase.
"""

from unittest.mock import MagicMock

import pytest

from dddguard.scanner.detection.ports.driving.facade import DetectionFacade
from dddguard.scanner.detection.ports.errors import InvalidScanPathError
from dddguard.shared.domain import CodeGraph, ScannerConfig

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_scan_uc():
    return MagicMock()


@pytest.fixture
def facade(mock_scan_uc) -> DetectionFacade:
    return DetectionFacade(scan_use_case=mock_scan_uc)


@pytest.fixture
def scanner_config() -> ScannerConfig:
    return ScannerConfig()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDetectionFacadeHappyPath:
    def test_delegates_to_use_case(self, facade, mock_scan_uc, tmp_path, scanner_config):
        """scan_physical_project should forward to the use case."""
        target = tmp_path / "project"
        target.mkdir()

        expected_graph = CodeGraph()
        mock_scan_uc.return_value = expected_graph

        result = facade.scan_physical_project(
            scanner_config=scanner_config,
            target_path=target,
            scan_all=True,
        )

        assert result is expected_graph
        mock_scan_uc.assert_called_once_with(
            scanner_config=scanner_config,
            target_path=target,
            scan_all=True,
        )


class TestDetectionFacadePathValidation:
    def test_raises_for_non_existent_path(self, facade, scanner_config, tmp_path):
        """If the target path doesn't exist, InvalidScanPathError is raised."""
        missing = tmp_path / "does_not_exist"

        with pytest.raises(InvalidScanPathError):
            facade.scan_physical_project(
                scanner_config=scanner_config,
                target_path=missing,
            )
