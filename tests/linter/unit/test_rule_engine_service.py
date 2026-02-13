"""
Unit tests for RuleEngineService — validates all 13 architectural rules.
"""

from dddguard.shared.domain import (
    DirectionEnum,
    LayerEnum,
    ScopeEnum,
)
from tests.linter.conftest import make_graph, make_node, make_passport

# ==============================================================================
# GROUP 1: INTERNAL RULES (Same Context)
# ==============================================================================


class TestRule01_DomainPurity:
    """Rule 1: Domain can only import Domain and Global."""

    def test_domain_can_import_domain(self, rule_engine):
        # domain/order.py -> domain/money_vo.py ✅
        source = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/domain/money_vo.py"}),
        )
        target = make_node(
            "src/ordering/domain/money_vo.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_domain_cannot_import_app(self, rule_engine):
        # domain/order.py -> app/create_order_uc.py ❌
        source = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/app/create_order_uc.py"}),
        )
        target = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Domain Purity"
        assert violations[0].severity == "error"

    def test_domain_cannot_import_ports(self, rule_engine):
        # domain/order.py -> ports/driving/facade.py ❌
        source = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Domain Purity"


class TestRule02_AppIsolation:
    """Rule 2: App can import App (interfaces), Domain, Global."""

    def test_app_can_import_domain(self, rule_engine):
        # app/create_order_uc.py -> domain/order.py ✅
        source = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_app_cannot_import_ports(self, rule_engine):
        # app/create_order_uc.py -> ports/driven/repo.py ❌
        source = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/ports/driven/repo.py"}),
        )
        target = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "App Isolation"


class TestRule03_DrivingPortBoundary:
    """Rule 3: Ports/Driving can import App, Domain, Ports/Driving (schemas), Global."""

    def test_driving_port_can_import_app(self, rule_engine):
        # ports/driving/facade.py -> app/create_order_uc.py ✅
        source = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/app/create_order_uc.py"}),
        )
        target = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driving_port_can_import_domain(self, rule_engine):
        # ports/driving/facade.py -> domain/order.py ✅
        source = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driving_port_cannot_import_driven_port(self, rule_engine):
        # ports/driving/facade.py -> ports/driven/repo.py ❌
        source = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/ports/driven/repo.py"}),
        )
        target = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Driving Port Boundary"


class TestRule04_DrivenPortBoundary:
    """Rule 4: Ports/Driven can import App (interfaces), Domain, Adapters/Driven (tools), Global."""

    def test_driven_port_can_import_app_interfaces(self, rule_engine):
        # ports/driven/repo.py -> app/interfaces.py ✅
        source = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/ordering/app/interfaces.py"}),
        )
        target = make_node(
            "src/ordering/app/interfaces.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driven_port_can_import_domain(self, rule_engine):
        # ports/driven/repo.py -> domain/order.py ✅
        source = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driven_port_can_import_driven_adapter(self, rule_engine):
        # ports/driven/repo.py -> adapters/driven/db_engine.py ✅
        source = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/ordering/adapters/driven/db_engine.py"}),
        )
        target = make_node(
            "src/ordering/adapters/driven/db_engine.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVEN),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driven_port_cannot_import_driving_port(self, rule_engine):
        # ports/driven/repo.py -> ports/driving/facade.py ❌
        source = make_node(
            "src/ordering/ports/driven/repo.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/ordering/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Driven Port Boundary"


class TestRule05_DrivingAdapterBoundary:
    """Rule 5: Adapters/Driving can import Ports/Driving (facades, schemas), Global."""

    def test_driving_adapter_can_import_driving_port(self, rule_engine):
        # adapters/driving/cli.py -> ports/driving/facade.py ✅
        source = make_node(
            "src/ordering/adapters/driving/cli.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/ordering/ports/driving/facade.py",
            passport=make_passport(layer=LayerEnum.PORTS, direction=DirectionEnum.DRIVING),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_driving_adapter_cannot_import_domain(self, rule_engine):
        # adapters/driving/cli.py -> domain/order.py ❌
        source = make_node(
            "src/ordering/adapters/driving/cli.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Driving Adapter Boundary"

    def test_driving_adapter_cannot_import_app(self, rule_engine):
        # adapters/driving/cli.py -> app/create_order_uc.py ❌
        source = make_node(
            "src/ordering/adapters/driving/cli.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVING),
            imports=frozenset({"src/ordering/app/create_order_uc.py"}),
        )
        target = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Driving Adapter Boundary"


class TestRule06_DrivenAdapterBoundary:
    """Rule 6: Adapters/Driven can import Global, Shared only (pure infrastructure)."""

    def test_driven_adapter_can_import_global(self, rule_engine):
        # adapters/driven/db_engine.py -> shared/config.py ✅
        source = make_node(
            "src/ordering/adapters/driven/db_engine.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/shared/config.py"}),
        )
        target = make_node(
            "src/shared/config.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                layer=LayerEnum.GLOBAL,
                direction=DirectionEnum.ANY,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0  # Shared is bypass

    def test_driven_adapter_cannot_import_domain(self, rule_engine):
        # adapters/driven/db_engine.py -> domain/order.py ❌
        source = make_node(
            "src/ordering/adapters/driven/db_engine.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVEN),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Driven Adapter Boundary"


class TestRule07_Composition:
    """Rule 7: Composition can import everything within context (bypass)."""

    def test_composition_can_import_domain(self, rule_engine):
        # provider.py -> domain/order.py ✅
        source = make_node(
            "src/ordering/provider.py",
            passport=make_passport(layer=LayerEnum.COMPOSITION, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0  # Composition bypasses internal rules

    def test_composition_can_import_app(self, rule_engine):
        # provider.py -> app/create_order_uc.py ✅
        source = make_node(
            "src/ordering/provider.py",
            passport=make_passport(layer=LayerEnum.COMPOSITION, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/app/create_order_uc.py"}),
        )
        target = make_node(
            "src/ordering/app/create_order_uc.py",
            passport=make_passport(layer=LayerEnum.APP, direction=DirectionEnum.NONE),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0


# ==============================================================================
# GROUP 2: FRACTAL RULES (Parent ↔ Child)
# ==============================================================================


class TestRule08_FractalUpstreamAccess:
    """Rule 8: Child -> Parent: can import Domain, App, Ports/Driven."""

    def test_child_can_import_parent_domain(self, rule_engine):
        # detection/app/scan.py -> scanner/domain/value_objects.py ✅
        source = make_node(
            "src/scanner/detection/app/scan.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/domain/value_objects.py"}),
        )
        target = make_node(
            "src/scanner/domain/value_objects.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_child_can_import_parent_app(self, rule_engine):
        # detection/app/scan.py -> scanner/app/interfaces.py ✅
        source = make_node(
            "src/scanner/detection/app/scan.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/app/interfaces.py"}),
        )
        target = make_node(
            "src/scanner/app/interfaces.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_child_can_import_parent_driven_port(self, rule_engine):
        # detection/app/scan.py -> scanner/ports/driven/repo.py ✅
        source = make_node(
            "src/scanner/detection/app/scan.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/ports/driven/repo.py"}),
        )
        target = make_node(
            "src/scanner/ports/driven/repo.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVEN,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_child_cannot_import_parent_driving_port(self, rule_engine):
        # detection/app/scan.py -> scanner/ports/driving/facade.py ❌
        source = make_node(
            "src/scanner/detection/app/scan.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/ports/driving/facade.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Fractal Upstream Access"

    def test_child_cannot_import_parent_adapter(self, rule_engine):
        # detection/app/scan.py -> scanner/adapters/driving/cli.py ❌
        source = make_node(
            "src/scanner/detection/app/scan.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/adapters/driving/cli.py"}),
        )
        target = make_node(
            "src/scanner/adapters/driving/cli.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.ADAPTERS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Fractal Upstream Access"


class TestRule09_FractalDownstreamAccess:
    """Rule 9: Parent -> Child: can only import Ports/Driving (facades)."""

    def test_parent_can_import_child_driving_port(self, rule_engine):
        # scanner/app/run_scan.py -> detection/ports/driving/facade.py ✅
        source = make_node(
            "src/scanner/app/run_scan.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/detection/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/detection/ports/driving/facade.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_parent_cannot_import_child_domain(self, rule_engine):
        # scanner/app/run_scan.py -> detection/domain/parser.py ❌
        source = make_node(
            "src/scanner/app/run_scan.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/detection/domain/parser.py"}),
        )
        target = make_node(
            "src/scanner/detection/domain/parser.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Fractal Downstream Access"

    def test_parent_cannot_import_child_app(self, rule_engine):
        # scanner/app/run_scan.py -> detection/app/scan_uc.py ❌
        source = make_node(
            "src/scanner/app/run_scan.py",
            passport=make_passport(
                context_name="scanner",
                macro_zone=None,
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/detection/app/scan_uc.py"}),
        )
        target = make_node(
            "src/scanner/detection/app/scan_uc.py",
            passport=make_passport(
                context_name="detection",
                macro_zone="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Fractal Downstream Access"


# ==============================================================================
# GROUP 3: CROSS-CONTEXT RULES (Alien Contexts)
# ==============================================================================


class TestRule10_CrossContextOutbound:
    """Rule 10: Only Ports/Driven (ACL) can initiate calls to other contexts."""

    def test_acl_can_call_foreign_context(self, rule_engine):
        # linter/ports/driven/acl/scanner.py -> scanner/ports/driving/facade.py ✅
        source = make_node(
            "src/linter/ports/driven/acl/scanner.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVEN,
            ),
            imports=frozenset({"src/scanner/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/ports/driving/facade.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_app_cannot_call_foreign_context_directly(self, rule_engine):
        # linter/app/check_project_uc.py -> scanner/ports/driving/facade.py ❌
        source = make_node(
            "src/linter/app/check_project_uc.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/ports/driving/facade.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Cross-Context Outbound"

    def test_domain_cannot_call_foreign_context(self, rule_engine):
        # linter/domain/engine.py -> scanner/ports/driving/facade.py ❌
        source = make_node(
            "src/linter/domain/engine.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/scanner/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/ports/driving/facade.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Cross-Context Outbound"


class TestRule11_CrossContextInbound:
    """Rule 11: Can only call Ports/Driving of other contexts."""

    def test_can_access_foreign_driving_port(self, rule_engine):
        # linter/ports/driven/acl.py -> scanner/ports/driving/facade.py ✅
        source = make_node(
            "src/linter/ports/driven/acl.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVEN,
            ),
            imports=frozenset({"src/scanner/ports/driving/facade.py"}),
        )
        target = make_node(
            "src/scanner/ports/driving/facade.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVING,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_cannot_access_foreign_domain(self, rule_engine):
        # linter/ports/driven/acl.py -> scanner/domain/value_objects.py ❌
        source = make_node(
            "src/linter/ports/driven/acl.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVEN,
            ),
            imports=frozenset({"src/scanner/domain/value_objects.py"}),
        )
        target = make_node(
            "src/scanner/domain/value_objects.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Cross-Context Inbound"

    def test_cannot_access_foreign_app(self, rule_engine):
        # linter/ports/driven/acl.py -> scanner/app/run_scan_uc.py ❌
        source = make_node(
            "src/linter/ports/driven/acl.py",
            passport=make_passport(
                context_name="linter",
                layer=LayerEnum.PORTS,
                direction=DirectionEnum.DRIVEN,
            ),
            imports=frozenset({"src/scanner/app/run_scan_uc.py"}),
        )
        target = make_node(
            "src/scanner/app/run_scan_uc.py",
            passport=make_passport(
                context_name="scanner",
                layer=LayerEnum.APP,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Cross-Context Inbound"


# ==============================================================================
# GROUP 4: SCOPE ISOLATION RULES
# ==============================================================================


class TestRule12_SharedIndependence:
    """Rule 12: Shared cannot import from bounded contexts or root."""

    def test_shared_can_import_shared(self, rule_engine):
        # shared/domain/money_vo.py -> shared/helpers/utils.py ✅
        source = make_node(
            "src/shared/domain/money_vo.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                context_name=None,
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/shared/helpers/utils.py"}),
        )
        target = make_node(
            "src/shared/helpers/utils.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                context_name=None,
                layer=LayerEnum.GLOBAL,
                direction=DirectionEnum.ANY,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0

    def test_shared_cannot_import_context(self, rule_engine):
        # shared/domain/money_vo.py -> ordering/domain/order.py ❌
        source = make_node(
            "src/shared/domain/money_vo.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                context_name=None,
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/ordering/domain/order.py"}),
        )
        target = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(
                scope=ScopeEnum.CONTEXT,
                context_name="ordering",
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Shared Independence"

    def test_shared_cannot_import_root(self, rule_engine):
        # shared/domain/money_vo.py -> root/composition.py ❌
        source = make_node(
            "src/shared/domain/money_vo.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                context_name=None,
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
            imports=frozenset({"src/root/composition.py"}),
        )
        target = make_node(
            "src/root/composition.py",
            passport=make_passport(
                scope=ScopeEnum.ROOT,
                context_name=None,
                layer=LayerEnum.COMPOSITION,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 1
        assert violations[0].rule_name == "Shared Independence"


# ==============================================================================
# BYPASS CONDITIONS
# ==============================================================================


class TestBypassConditions:
    """Test bypass scenarios where rules are skipped."""

    def test_any_layer_can_import_shared(self, rule_engine):
        # domain/order.py -> shared/domain/money_vo.py ✅ (bypass)
        source = make_node(
            "src/ordering/domain/order.py",
            passport=make_passport(layer=LayerEnum.DOMAIN, direction=DirectionEnum.NONE),
            imports=frozenset({"src/shared/domain/money_vo.py"}),
        )
        target = make_node(
            "src/shared/domain/money_vo.py",
            passport=make_passport(
                scope=ScopeEnum.SHARED,
                context_name=None,
                layer=LayerEnum.DOMAIN,
                direction=DirectionEnum.NONE,
            ),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0  # Shared is always allowed

    def test_composition_bypasses_internal_rules(self, rule_engine):
        # provider.py -> adapters/driving/cli.py ✅ (bypass)
        source = make_node(
            "src/ordering/provider.py",
            passport=make_passport(layer=LayerEnum.COMPOSITION, direction=DirectionEnum.NONE),
            imports=frozenset({"src/ordering/adapters/driving/cli.py"}),
        )
        target = make_node(
            "src/ordering/adapters/driving/cli.py",
            passport=make_passport(layer=LayerEnum.ADAPTERS, direction=DirectionEnum.DRIVING),
        )
        graph = make_graph(source, target)

        violations = rule_engine.check_node(source, graph)
        assert len(violations) == 0  # Composition bypasses
