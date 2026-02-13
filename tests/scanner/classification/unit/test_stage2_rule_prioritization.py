from unittest.mock import patch

import pytest

from dddguard.scanner.classification.domain.services.stage2_rule_prioritization import (
    Stage2RulePrioritizationService,
)
from dddguard.shared.domain import (
    ArchetypeType,
    DirectionEnum,
    LayerEnum,
)

# Alias for brevity in test data
TYPE_SERVICE = ArchetypeType.ASSET
TYPE_HELPER = ArchetypeType.HELPER
TYPE_REPO = ArchetypeType.MARKER


class TestStage2RulePrioritizationService:
    @pytest.fixture
    def service(self):
        return Stage2RulePrioritizationService

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """
        CRITICAL: Clears the LRU cache before every test.
        Since we mock the underlying registries, we must force the service
        to re-compute the pool instead of returning a stale cached result
        from a previous test run.
        """
        Stage2RulePrioritizationService._build_prioritized_pool.cache_clear()
        return

    def test_layer_weight_priority(self, service):
        """
        Scenario: Two rules match. One in DOMAIN (High Priority), one in GLOBAL (Low Priority).
        Expectation: DOMAIN rule comes first in the list.
        """
        mock_registry = {
            LayerEnum.DOMAIN: {DirectionEnum.NONE: {TYPE_SERVICE: ["domain_rule"]}},
            LayerEnum.GLOBAL: {DirectionEnum.ANY: {TYPE_HELPER: ["global_rule"]}},
        }

        with (
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_NAMING_REGISTRY",
                mock_registry,
            ),
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_STRUCTURAL_REGISTRY",
                {},
            ),
        ):
            # Act
            pool = service.get_applicable_rules(LayerEnum.DOMAIN, DirectionEnum.NONE)

            # Assert
            assert len(pool) == 2

            # First item must be DOMAIN (Weight 1)
            assert pool[0].origin_layer == LayerEnum.DOMAIN
            assert pool[0].regex == "domain_rule"

            # Second item must be GLOBAL (Weight 10)
            assert pool[1].origin_layer == LayerEnum.GLOBAL
            assert pool[1].regex == "global_rule"

    def test_regex_length_priority(self, service):
        """
        Scenario: Within the SAME layer, we have a short regex and a long (specific) regex.
        Expectation: The longer regex comes first.
        """
        mock_registry = {
            LayerEnum.APP: {
                DirectionEnum.NONE: {
                    TYPE_SERVICE: [
                        "service$",  # Len 8
                        "^create_user_service$",  # Len 21 (Should be first)
                    ]
                }
            }
        }

        with (
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_NAMING_REGISTRY",
                mock_registry,
            ),
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_STRUCTURAL_REGISTRY",
                {},
            ),
        ):
            pool = service.get_applicable_rules(LayerEnum.APP, DirectionEnum.NONE)

            assert len(pool) == 2
            assert pool[0].regex == "^create_user_service$"
            assert pool[1].regex == "service$"

    def test_direction_filtering(self, service):
        """
        Scenario: Requesting rules for DRIVING direction.
        Expectation:
        - DRIVING rules are Included.
        - ANY rules are Included.
        - DRIVEN rules are Excluded.
        - NONE rules are Excluded.
        """
        mock_registry = {
            LayerEnum.ADAPTERS: {
                DirectionEnum.DRIVING: {TYPE_SERVICE: ["driving_rule"]},
                DirectionEnum.DRIVEN: {TYPE_SERVICE: ["driven_rule"]},
                DirectionEnum.ANY: {TYPE_SERVICE: ["any_rule"]},
                DirectionEnum.NONE: {TYPE_SERVICE: ["none_rule"]},
            }
        }

        with (
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_NAMING_REGISTRY",
                mock_registry,
            ),
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_STRUCTURAL_REGISTRY",
                {},
            ),
        ):
            pool = service.get_applicable_rules(LayerEnum.ADAPTERS, DirectionEnum.DRIVING)

            # Collect all regexes in the result for easy checking
            found_regexes = {r.regex for r in pool}

            assert "driving_rule" in found_regexes
            assert "any_rule" in found_regexes
            assert "driven_rule" not in found_regexes
            assert "none_rule" not in found_regexes

    def test_undefined_direction_filtering(self, service):
        """
        Scenario: Direction is UNDEFINED (e.g. Domain layer).
        Expectation: Include NONE and ANY. Exclude DRIVING/DRIVEN.
        """
        mock_registry = {
            LayerEnum.DOMAIN: {
                DirectionEnum.DRIVING: {TYPE_SERVICE: ["driving_rule"]},
                DirectionEnum.NONE: {TYPE_SERVICE: ["none_rule"]},
                DirectionEnum.ANY: {TYPE_SERVICE: ["any_rule"]},
            }
        }

        with (
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_NAMING_REGISTRY",
                mock_registry,
            ),
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_STRUCTURAL_REGISTRY",
                {},
            ),
        ):
            pool = service.get_applicable_rules(LayerEnum.DOMAIN, DirectionEnum.UNDEFINED)
            found_regexes = {r.regex for r in pool}

            assert "none_rule" in found_regexes
            assert "any_rule" in found_regexes
            assert "driving_rule" not in found_regexes

    def test_combines_structural_and_naming_registries(self, service):
        """
        Scenario: Rules exist in both folder-based (Structural) and filename-based (Naming) registries.
        Expectation: Both sets of rules are merged into the pool.
        """
        naming_mock = {LayerEnum.DOMAIN: {DirectionEnum.NONE: {TYPE_SERVICE: ["naming_rule"]}}}
        structural_mock = {LayerEnum.DOMAIN: {DirectionEnum.NONE: {TYPE_REPO: ["structural_rule"]}}}

        with (
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_NAMING_REGISTRY",
                naming_mock,
            ),
            patch(
                "dddguard.scanner.classification.domain.services.stage2_rule_prioritization.DDD_STRUCTURAL_REGISTRY",
                structural_mock,
            ),
        ):
            pool = service.get_applicable_rules(LayerEnum.DOMAIN, DirectionEnum.NONE)
            found_regexes = {r.regex for r in pool}

            assert "naming_rule" in found_regexes
            assert "structural_rule" in found_regexes
