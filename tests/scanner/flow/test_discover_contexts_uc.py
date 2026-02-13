"""
Flow tests for DiscoverContextsUseCase.

Pipeline:
  1. Detection  (mocked)
  2. Classification  (mocked)
  3. Aggregation & Deduplication  (real logic)
  4. Sorting  (real logic — root first, shared second, biz alphabetical)
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dddguard.scanner.app.use_cases.discover_contexts_uc import DiscoverContextsUseCase
from dddguard.shared.domain import (
    CodeGraph,
    ScannerConfig,
)
from tests.scanner.conftest import make_classified_graph, make_passport

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
def use_case(detection_gateway, classification_gateway) -> DiscoverContextsUseCase:
    return DiscoverContextsUseCase(
        detection_gateway=detection_gateway,
        classification_gateway=classification_gateway,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDiscoverContextsHappyPath:
    def test_three_contexts_discovered_and_sorted(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """root -> shared -> billing (alphabetical among biz contexts)."""
        classified = make_classified_graph(
            [
                {"path": "root.cli", "passport": make_passport(context_name="root")},
                {
                    "path": "shared.utils",
                    "passport": make_passport(context_name="shared"),
                },
                {
                    "path": "billing.domain.order",
                    "passport": make_passport(context_name="billing"),
                },
            ]
        )

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
        )

        assert len(result) == 3
        assert result[0].context_name == "root"
        assert result[1].context_name == "shared"
        assert result[2].context_name == "billing"


class TestDiscoverContextsDeduplication:
    def test_duplicate_contexts_are_deduplicated(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """Multiple nodes in the same context produce only one entry."""
        classified = make_classified_graph(
            [
                {
                    "path": "billing.domain.order",
                    "passport": make_passport(context_name="billing"),
                },
                {
                    "path": "billing.domain.item",
                    "passport": make_passport(context_name="billing"),
                },
                {
                    "path": "billing.app.create",
                    "passport": make_passport(context_name="billing"),
                },
            ]
        )

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(scanner_config=scanner_config, source_dir=source_dir)

        assert len(result) == 1
        assert result[0].context_name == "billing"


class TestDiscoverContextsSkipsInvalid:
    def test_nodes_without_passport_are_skipped(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """Nodes that were never classified should be silently skipped."""
        graph = CodeGraph()
        # Classified node
        node_ok = graph.add_node("billing.domain.order")
        node_ok.link_imports([])
        node_ok.classify(make_passport(context_name="billing"))
        # Unclassified node (no passport)
        graph.add_node("broken.module")

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = graph

        result = use_case(scanner_config=scanner_config, source_dir=source_dir)

        assert len(result) == 1
        assert result[0].context_name == "billing"

    def test_nodes_without_context_name_are_skipped(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """Nodes with passport but context_name=None are skipped."""
        classified = make_classified_graph(
            [
                {
                    "path": "unknown.module",
                    "passport": make_passport(context_name=None),
                },
                {
                    "path": "billing.x",
                    "passport": make_passport(context_name="billing"),
                },
            ]
        )

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(scanner_config=scanner_config, source_dir=source_dir)

        assert len(result) == 1
        assert result[0].context_name == "billing"


class TestDiscoverContextsEmptyGraph:
    def test_empty_graph_returns_empty_list(
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

        assert result == []
