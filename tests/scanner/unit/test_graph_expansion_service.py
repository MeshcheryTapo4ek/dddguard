from dataclasses import dataclass, field

import pytest

from dddguard.scanner.domain.graph_expansion_service import GraphExpansionService

# --- MOCKS ---


@dataclass
class MockNode:
    """
    Simulates a generic Node in the Graph.
    We don't need SourceFileVo here, just an object with 'imports'.
    """

    imports: set[str] = field(default_factory=set)


@dataclass
class MockGraph:
    """Simulates CodeGraph."""

    nodes: dict[str, MockNode] = field(default_factory=dict)


# --- TESTS ---


class TestGraphExpansionService:
    @pytest.fixture
    def service(self):
        return GraphExpansionService

    @pytest.fixture
    def simple_chain_graph(self) -> MockGraph:
        """
        A -> B -> C -> D
        """
        return MockGraph(
            nodes={
                "A": MockNode(imports={"B"}),
                "B": MockNode(imports={"C"}),
                "C": MockNode(imports={"D"}),
                "D": MockNode(imports=set()),
            }
        )

    @pytest.fixture
    def cyclic_graph(self) -> MockGraph:
        """
        A -> B -> A (Cycle)
        A -> C
        """
        return MockGraph(
            nodes={
                "A": MockNode(imports={"B", "C"}),
                "B": MockNode(imports={"A"}),
                "C": MockNode(imports=set()),
            }
        )

    def test_depth_zero_returns_initial(self, service, simple_chain_graph):
        """Depth 0 should return strictly the input set."""
        initial = {"A"}
        result = service.expand(simple_chain_graph, initial, depth=0)
        assert result == {"A"}

    def test_depth_one_direct_neighbors(self, service, simple_chain_graph):
        """Depth 1 should include A and B."""
        initial = {"A"}
        result = service.expand(simple_chain_graph, initial, depth=1)
        assert result == {"A", "B"}

    def test_depth_two_transitive(self, service, simple_chain_graph):
        """Depth 2 should include A, B, and C."""
        initial = {"A"}
        result = service.expand(simple_chain_graph, initial, depth=2)
        assert result == {"A", "B", "C"}

    def test_full_chain_expansion(self, service, simple_chain_graph):
        """Large depth should capture everything reachable."""
        initial = {"A"}
        result = service.expand(simple_chain_graph, initial, depth=10)
        assert result == {"A", "B", "C", "D"}

    def test_cyclic_dependencies_safe(self, service, cyclic_graph):
        """Service should not hang on cycles (A->B->A)."""
        initial = {"A"}
        result = service.expand(cyclic_graph, initial, depth=5)

        # Should find A, B, C.
        # Should NOT hang in infinite loop.
        assert result == {"A", "B", "C"}

    def test_missing_node_graceful_handling(self, service):
        """
        A -> B (but B is not in graph nodes dict for some reason).
        Should not crash.
        """
        graph = MockGraph(
            nodes={
                "A": MockNode(imports={"B"}),
                # B is missing from keys (Broken Link)
            }
        )
        initial = {"A"}

        result = service.expand(graph, initial, depth=1)
        # B cannot be visited or added because it doesn't exist in graph
        # Result contains A.
        # Note: Depending on logic, B might be added to result set but ignored in queue.
        # But our logic checks `current_node = graph.nodes.get`.
        # So B is added to queue, popped, lookup fails, continue.
        # B IS added to visible set in the loop before queuing.
        # Let's verify behavior:
        # A imports B. B not in visited. Add B to visible. Queue B.
        # Pop B. Lookup B -> None. Continue.
        assert "B" in result
