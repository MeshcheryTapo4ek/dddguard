"""
Flow tests for RunScanUseCase.

This use case orchestrates the 5-stage pipeline:
  1. Detection  (via IDetectionGateway)
  2. Classification  (via IClassificationGateway)
  3. Filtering  (GraphFilteringService — static, not mocked)
  4. Expansion  (GraphExpansionService — static, not mocked)
  5. Pruning  (GraphFilteringService.prune_graph — static, not mocked)

We mock only the two gateway interfaces; the domain services are exercised directly.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dddguard.scanner.app.use_cases.run_scan_uc import RunScanUseCase
from dddguard.shared.domain import (
    CodeGraph,
    NodeStatus,
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
def use_case(detection_gateway, classification_gateway) -> RunScanUseCase:
    return RunScanUseCase(
        detection_gateway=detection_gateway,
        classification_gateway=classification_gateway,
    )


def _build_classified_graph(source_dir: Path) -> CodeGraph:
    """Helper: builds a small classified graph located inside source_dir."""
    return make_classified_graph(
        [
            {
                "path": "billing.domain.order",
                "file_path": source_dir / "billing" / "domain" / "order.py",
                "passport": make_passport(context_name="billing"),
            },
            {
                "path": "billing.domain.item",
                "file_path": source_dir / "billing" / "domain" / "item.py",
                "passport": make_passport(context_name="billing"),
                "imports": {"billing.domain.order"},
            },
            {
                "path": "shared.helpers.utils",
                "file_path": source_dir / "shared" / "helpers" / "utils.py",
                "passport": make_passport(context_name="shared"),
            },
        ]
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRunScanUCHappyPath:
    def test_five_stage_pipeline_executes(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """
        Verifies the full pipeline: detect -> classify -> filter -> expand -> prune.
        """
        detected_graph = CodeGraph()
        detected_graph.add_node(
            "billing.domain.order", file_path=source_dir / "billing/domain/order.py"
        )

        classified = _build_classified_graph(source_dir)
        detection_gateway.scan.return_value = detected_graph
        classification_gateway.classify.return_value = classified

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
        )

        # Detection was called
        detection_gateway.scan.assert_called_once_with(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=False,
        )

        # Classification was called
        classification_gateway.classify.assert_called_once_with(
            graph=detected_graph,
            source_dir=source_dir,
        )

        # Nodes inside source_dir should be FINALIZED
        assert result is classified
        for node in result.nodes.values():
            assert node.status == NodeStatus.FINALIZED

    def test_parameters_forwarded_correctly(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """All user-specified parameters are forwarded to gateways."""
        classified = _build_classified_graph(source_dir)
        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
            scan_all=True,
            import_depth=0,
            whitelist_layers=["DOMAIN"],
            whitelist_contexts=["billing"],
        )

        detection_gateway.scan.assert_called_once_with(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=True,
        )


class TestRunScanUCExpansion:
    def test_import_depth_zero_no_expansion(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """
        depth=0: only nodes physically inside focus_path are visible.
        """
        classified = _build_classified_graph(source_dir)
        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
            import_depth=0,
            whitelist_contexts=["billing"],
        )

        finalized = {p for p, n in result.nodes.items() if n.status == NodeStatus.FINALIZED}
        # Only billing nodes should be visible
        assert "billing.domain.order" in finalized
        assert "billing.domain.item" in finalized
        assert "shared.helpers.utils" not in finalized

    def test_import_depth_positive_expands_dependencies(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """
        depth=1: visible nodes' imports are also revealed.
        """
        classified = make_classified_graph(
            [
                {
                    "path": "billing.domain.item",
                    "file_path": source_dir / "billing/domain/item.py",
                    "passport": make_passport(context_name="billing"),
                    "imports": {"shared.helpers.utils"},
                },
                {
                    "path": "shared.helpers.utils",
                    "file_path": source_dir / "shared/helpers/utils.py",
                    "passport": make_passport(context_name="shared"),
                },
            ]
        )

        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = classified

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
            import_depth=1,
            whitelist_contexts=["billing"],
        )

        finalized = {p for p, n in result.nodes.items() if n.status == NodeStatus.FINALIZED}
        # Billing node is directly visible; shared.helpers.utils is expanded via depth=1
        assert "billing.domain.item" in finalized
        assert "shared.helpers.utils" in finalized


class TestRunScanUCEmptyGraph:
    def test_empty_graph_still_completes(
        self,
        use_case,
        detection_gateway,
        classification_gateway,
        source_dir,
        scanner_config,
    ):
        """An empty detected graph should not crash the pipeline."""
        detection_gateway.scan.return_value = CodeGraph()
        classification_gateway.classify.return_value = CodeGraph()

        result = use_case(
            scanner_config=scanner_config,
            source_dir=source_dir,
        )

        assert result.total_files == 0
