"""
Flow tests for InspectTreeUseCase.

Pipeline:
  1. Detection  (mocked IDetectionGateway)
  2. Classification  (mocked IClassificationGateway)
  3. Finalization  (all nodes get FINALIZED — no filtering)
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dddguard.scanner.app.use_cases.inspect_tree_uc import InspectTreeUseCase
from dddguard.shared.domain import (
    CodeGraph,
    NodeStatus,
    ScannerConfig,
)
from dddguard.shared.helpers.generics.errors import GenericDomainError
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
def scanner_config() -> ScannerConfig:
    return ScannerConfig()


@pytest.fixture
def detection_gateway():
    return MagicMock()


@pytest.fixture
def classification_gateway():
    return MagicMock()


@pytest.fixture
def use_case(detection_gateway, classification_gateway) -> InspectTreeUseCase:
    return InspectTreeUseCase(
        detection_gateway=detection_gateway,
        classification_gateway=classification_gateway,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInspectTreeUCHappyPath:
    def test_all_nodes_finalized(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """All classified nodes should be FINALIZED after the pipeline."""
        classified = make_classified_graph(
            [
                {"path": "billing.domain.order"},
                {"path": "billing.app.create"},
                {"path": "shared.helpers.utils"},
            ]
        )

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
        )

        assert result is classified
        for node in result.nodes.values():
            assert node.status == NodeStatus.FINALIZED

    def test_gateways_called_with_correct_params(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        classified = make_classified_graph([{"path": "a.b"}])
        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        use_case(scanner_config=scanner_config, source_dir=source_dir, scan_all=True)

        detection_gateway.scan.assert_called_once_with(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=True,
        )
        classification_gateway.classify.assert_called_once()


class TestInspectTreeUCEmptyGraph:
    def test_empty_graph_returns_empty(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = CodeGraph()

        result = use_case(scanner_config=scanner_config, source_dir=source_dir)

        assert result.total_files == 0


class TestInspectTreeUCNodeWithoutPassport:
    def test_node_without_passport_raises_on_finalize(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """
        If a node arrives without a passport (classification bug),
        finalize() raises GenericDomainError.
        """
        graph = CodeGraph()
        node = graph.add_node("broken.node")
        # Node is DETECTED, never classified — no passport
        node.link_imports([])

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = graph

        with pytest.raises(GenericDomainError, match="missing passport"):
            use_case(scanner_config=scanner_config, source_dir=source_dir)
