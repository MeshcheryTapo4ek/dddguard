import pytest

from dddguard.scanner.classification.domain.services.stage2_rule_prioritization import (
    RuleCandidate,
)
from dddguard.scanner.classification.domain.services.stage3_4_component_matching import (
    Stage3_4ComponentMatchingService,
)
from dddguard.shared.domain import (
    AppType,
    ArchetypeType,
    DomainType,
    LayerEnum,
    MatchMethod,
    PortType,
)


class TestStage3_4ComponentMatchingService:
    @pytest.fixture
    def service(self):
        return Stage3_4ComponentMatchingService

    @pytest.fixture
    def mock_pool(self):
        """
        A simulated prioritized pool from Stage 2.
        Simulates a mix of rules for Domain, App, and Ports layers.

        Order matters: In a real scenario, this list comes sorted by Weight + Specificity.
        """
        return (
            # 1. ACL (Specific Port Rule)
            RuleCandidate(
                comp_type=PortType.ACL,
                regex="^acl$",
                weight=4,
                origin_layer=LayerEnum.PORTS,
            ),
            # 2. Use Case (App Rule)
            RuleCandidate(
                comp_type=AppType.USE_CASE,
                regex="^.*use_cases?$",
                weight=2,
                origin_layer=LayerEnum.APP,
            ),
            # 3. Domain Service (Domain Rule)
            RuleCandidate(
                comp_type=DomainType.DOMAIN_SERVICE,
                regex="^.*service$",
                weight=1,
                origin_layer=LayerEnum.DOMAIN,
            ),
            # 4. Facade (Port Rule - Naming convention)
            RuleCandidate(
                comp_type=PortType.FACADE,
                regex="^.*facade$",
                weight=4,
                origin_layer=LayerEnum.PORTS,
            ),
            # 5. Interface (App Rule)
            RuleCandidate(
                comp_type=AppType.INTERFACE,
                regex="^interfaces?$",
                weight=2,
                origin_layer=LayerEnum.APP,
            ),
        )

    def test_match_acl_structural(self, service, mock_pool):
        """
        Scenario: Path contains 'acl' folder.
        Expectation: Identified as ACL (PortType) via STRUCTURAL match.
        """
        # tokens from path: src/context/ports/acl/github_adapter.py
        # 'ports' is filtered out by Stage 1, leaving 'acl', 'github_adapter'
        tokens = ["acl", "github_adapter"]
        filename = "github_adapter"

        comp_type, method, layer = service.match_component(mock_pool, tokens, filename)

        assert comp_type == PortType.ACL
        assert method == MatchMethod.STRUCTURAL
        assert layer == LayerEnum.PORTS

    def test_match_facade_naming(self, service, mock_pool):
        """
        Scenario: Filename is 'payment_facade.py'.
        Expectation: Identified as FACADE (PortType) via NAME match.
        """
        tokens = ["driving", "web"]  # No structural match in pool
        filename = "payment_facade"

        comp_type, method, layer = service.match_component(mock_pool, tokens, filename)

        assert comp_type == PortType.FACADE
        assert method == MatchMethod.NAME
        assert layer == LayerEnum.PORTS

    def test_match_use_case_structural(self, service, mock_pool):
        """
        Scenario: File located in 'use_cases' folder.
        Expectation: Identified as USE_CASE (AppType).
        """
        tokens = ["use_cases", "create_order"]
        filename = "create_order"

        comp_type, method, layer = service.match_component(mock_pool, tokens, filename)

        assert comp_type == AppType.USE_CASE
        assert method == MatchMethod.STRUCTURAL
        assert layer == LayerEnum.APP

    def test_match_domain_service_naming(self, service, mock_pool):
        """
        Scenario: Filename 'pricing_service' in a generic domain folder.
        Expectation: Identified as DOMAIN_SERVICE.
        """
        tokens = ["model"]  # 'model' is not in our mock pool
        filename = "pricing_service"

        comp_type, method, layer = service.match_component(mock_pool, tokens, filename)

        assert comp_type == DomainType.DOMAIN_SERVICE
        assert method == MatchMethod.NAME
        assert layer == LayerEnum.DOMAIN

    def test_structural_priority_over_naming(self, service, mock_pool):
        """
        Scenario: A file 'user_service.py' inside an 'interfaces' folder.

        Conflict:
        - Structural: 'interfaces' -> AppType.INTERFACE
        - Naming: 'user_service' -> DomainType.DOMAIN_SERVICE

        Expectation: Structural Match (Stage 3) always wins over Naming (Stage 4).
        It is an Interface *named* like a service, but physically it lives in interfaces.
        """
        tokens = ["interfaces"]
        filename = "user_service"

        comp_type, method, _ = service.match_component(mock_pool, tokens, filename)

        # Structural 'interfaces' check happens in Stage 3
        assert comp_type == AppType.INTERFACE
        assert method == MatchMethod.STRUCTURAL
        # Naming check (Stage 4) is skipped because Stage 3 succeeded

    def test_no_match_fallback(self, service, mock_pool):
        """
        Scenario: Random file 'utils.py' in 'helpers' folder (not in our mock pool).
        Expectation: UNKNOWN / UNDEFINED.
        """
        tokens = ["helpers"]
        filename = "utils"

        comp_type, method, layer = service.match_component(mock_pool, tokens, filename)

        assert comp_type == ArchetypeType.UNKNOWN
        assert method == MatchMethod.UNKNOWN
        assert layer == LayerEnum.UNDEFINED
