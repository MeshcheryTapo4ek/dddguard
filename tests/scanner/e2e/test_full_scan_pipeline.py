"""
End-to-End test for the full Scanner pipeline.

Creates a realistic Python project tree on disk and runs the complete pipeline:
  Detection (real FileSystemRepository)
  -> Classification (real IdentifyComponentUseCase)
  -> Filtering (GraphFilteringService)
  -> Expansion (GraphExpansionService)
  -> Pruning

No mocks — exercises the entire stack from filesystem to classified graph.
"""

from pathlib import Path

import pytest

# Classification
from dddguard.scanner.classification.app.classify_graph_workflow import (
    ClassifyGraphWorkflow,
)
from dddguard.scanner.classification.app.identify_component_uc import (
    IdentifyComponentUseCase,
)

# Detection
from dddguard.scanner.detection.app.scan_project_uc import ScanProjectUseCase
from dddguard.scanner.detection.ports.driven.storage.file_system_repository import (
    FileSystemRepository,
)

# Domain Services
from dddguard.scanner.domain import GraphExpansionService, GraphFilteringService
from dddguard.shared.domain import (
    LayerEnum,
    NodeStatus,
    ScannerConfig,
)

# ---------------------------------------------------------------------------
# Project Layout Builder
# ---------------------------------------------------------------------------


def _create_project_tree(root: Path) -> Path:
    """
    Creates the following project structure inside ``root``:

    src/
      billing/
        __init__.py
        domain/
          __init__.py
          order.py          (imports item)
          item.py
        app/
          __init__.py
          create_order.py   (imports domain.order)
        ports/
          __init__.py
          driving/
            __init__.py
            facade.py
      shared/
        __init__.py
        helpers/
          __init__.py
          utils.py
    """
    src = root / "src"

    # --- billing context ---
    billing = src / "billing"
    (billing / "domain").mkdir(parents=True)
    (billing / "app").mkdir(parents=True)
    (billing / "ports" / "driving").mkdir(parents=True)

    (billing / "__init__.py").write_text("")
    (billing / "domain" / "__init__.py").write_text("")
    (billing / "domain" / "order.py").write_text(
        "from billing.domain.item import Item\n\nclass Order:\n    pass\n"
    )
    (billing / "domain" / "item.py").write_text("class Item:\n    pass\n")
    (billing / "app" / "__init__.py").write_text("")
    (billing / "app" / "create_order.py").write_text(
        "from billing.domain.order import Order\n\ndef create_order(): ...\n"
    )
    (billing / "ports" / "__init__.py").write_text("")
    (billing / "ports" / "driving" / "__init__.py").write_text("")
    (billing / "ports" / "driving" / "facade.py").write_text("class BillingFacade:\n    pass\n")

    # --- shared context ---
    shared = src / "shared"
    (shared / "helpers").mkdir(parents=True)

    (shared / "__init__.py").write_text("")
    (shared / "helpers" / "__init__.py").write_text("")
    (shared / "helpers" / "utils.py").write_text("def helper(): ...\n")

    return src


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path) -> Path:
    return tmp_path


@pytest.fixture
def source_dir(project_root) -> Path:
    return _create_project_tree(project_root)


@pytest.fixture
def scanner_config() -> ScannerConfig:
    return ScannerConfig()


# ---------------------------------------------------------------------------
# E2E Tests
# ---------------------------------------------------------------------------


class TestFullScanPipeline:
    """Runs the complete pipeline against a real filesystem."""

    def test_detection_produces_nodes_with_imports(self, source_dir, scanner_config):
        """Phase 1: Detection should discover files and resolve import links."""
        repo = FileSystemRepository()
        scan_uc = ScanProjectUseCase(project_reader=repo)

        graph = scan_uc(
            scanner_config=scanner_config,
            target_path=source_dir,
        )

        # Should find multiple files
        assert graph.total_files >= 5

        # order.py should have an import link to item
        order_node = graph.get_node("billing.domain.order")
        assert order_node is not None
        assert order_node.status == NodeStatus.LINKED
        assert any("item" in imp for imp in order_node.imports)

    def test_classification_assigns_passports(self, source_dir, scanner_config):
        """Phase 2: Classification should assign passports to all nodes."""
        repo = FileSystemRepository()
        scan_uc = ScanProjectUseCase(project_reader=repo)
        graph = scan_uc(scanner_config=scanner_config, target_path=source_dir)

        identifier = IdentifyComponentUseCase()
        workflow = ClassifyGraphWorkflow(identifier_use_case=identifier)
        classified = workflow(graph=graph, source_dir=source_dir)

        assert classified.classified_count == classified.total_files

        for node in classified.nodes.values():
            assert node.status == NodeStatus.CLASSIFIED
            assert node.passport is not None

        # Spot-check: order.py should be in billing context, domain layer
        order_node = classified.get_node("billing.domain.order")
        assert order_node is not None
        assert order_node.passport.context_name == "billing"
        assert order_node.passport.layer == LayerEnum.DOMAIN

    def test_filtering_narrows_to_billing_context(self, source_dir, scanner_config):
        """Phase 3: Filtering with whitelist_contexts=['billing'] hides shared."""
        repo = FileSystemRepository()
        scan_uc = ScanProjectUseCase(project_reader=repo)
        graph = scan_uc(scanner_config=scanner_config, target_path=source_dir)

        identifier = IdentifyComponentUseCase()
        workflow = ClassifyGraphWorkflow(identifier_use_case=identifier)
        classified = workflow(graph=graph, source_dir=source_dir)

        visible = GraphFilteringService.determine_initial_focus(
            graph=classified,
            focus_path=source_dir,
            whitelist_layers=None,
            whitelist_contexts=["billing"],
        )

        # Only billing nodes should be visible
        for path in visible:
            node = classified.get_node(path)
            assert node.passport.context_name == "billing"

        # shared should NOT be visible
        shared_paths = [p for p in classified.nodes if p.startswith("shared.")]
        for sp in shared_paths:
            assert sp not in visible

    def test_expansion_reveals_dependencies(self, source_dir, scanner_config):
        """Phase 4: Expansion with depth=1 reveals imports of visible nodes."""
        repo = FileSystemRepository()
        scan_uc = ScanProjectUseCase(project_reader=repo)
        graph = scan_uc(scanner_config=scanner_config, target_path=source_dir)

        identifier = IdentifyComponentUseCase()
        workflow = ClassifyGraphWorkflow(identifier_use_case=identifier)
        classified = workflow(graph=graph, source_dir=source_dir)

        # Focus only on billing.app
        billing_app_path = source_dir / "billing" / "app"
        initial_visible = GraphFilteringService.determine_initial_focus(
            graph=classified,
            focus_path=billing_app_path,
            whitelist_layers=None,
            whitelist_contexts=None,
        )

        expanded = GraphExpansionService.expand(
            graph=classified,
            initial_visible=initial_visible,
            depth=1,
        )

        # expanded should be a superset of initial
        assert expanded >= initial_visible

    def test_full_pipeline_end_to_end(self, source_dir, scanner_config):
        """Complete pipeline: detect -> classify -> filter -> expand -> prune."""
        repo = FileSystemRepository()
        scan_uc = ScanProjectUseCase(project_reader=repo)
        graph = scan_uc(scanner_config=scanner_config, target_path=source_dir)

        identifier = IdentifyComponentUseCase()
        workflow = ClassifyGraphWorkflow(identifier_use_case=identifier)
        classified = workflow(graph=graph, source_dir=source_dir)

        # Filter: everything
        visible = GraphFilteringService.determine_initial_focus(
            graph=classified,
            focus_path=source_dir,
            whitelist_layers=None,
            whitelist_contexts=None,
        )

        # Expand
        expanded = GraphExpansionService.expand(
            graph=classified,
            initial_visible=visible,
            depth=0,
        )

        # Prune
        finalized = GraphFilteringService.prune_graph(
            graph=classified,
            visible_modules=expanded,
        )

        # All visible nodes should be FINALIZED
        for path in finalized:
            assert classified.nodes[path].status == NodeStatus.FINALIZED

        # There should be FINALIZED nodes
        assert len(finalized) > 0
        assert classified.coverage_percent > 0
