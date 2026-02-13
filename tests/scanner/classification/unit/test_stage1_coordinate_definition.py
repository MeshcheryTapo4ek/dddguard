import pytest

from dddguard.scanner.classification.domain.services.stage1_coordinate_definition import (
    Stage1CoordinateDefinitionService,
)
from dddguard.scanner.classification.domain.value_objects import ContextBoundaryVo
from dddguard.shared.domain import DirectionEnum, LayerEnum, ScopeEnum


class TestStage1CoordinateDefinitionService:
    @pytest.fixture
    def service(self):
        return Stage1CoordinateDefinitionService

    def _make_boundary(
        self,
        parts: tuple[str, ...],
        layer: LayerEnum,
        scope: ScopeEnum = ScopeEnum.CONTEXT,
    ) -> ContextBoundaryVo:
        """Helper to reduce boilerplate in tests."""
        return ContextBoundaryVo(
            scope=scope,
            macro_path="test",
            context_name="ctx",
            effective_parts=parts,
            detected_layer_token=layer,
        )

    def test_direction_driving_standard(self, service):
        parts = ("adapters", "driving", "user_controller")
        boundary = self._make_boundary(parts, LayerEnum.ADAPTERS)

        # FIXED: Called define_coordinates instead of get_applicable_rules
        result = service.define_coordinates(boundary)

        assert result.direction == DirectionEnum.DRIVING
        assert result.layer == LayerEnum.ADAPTERS
        assert result.searchable_tokens == ["user_controller"]

    def test_direction_driven_alias(self, service):
        parts = ("infrastructure", "outbound", "postgres_repo")
        boundary = self._make_boundary(parts, LayerEnum.ADAPTERS)

        result = service.define_coordinates(boundary)

        assert result.direction == DirectionEnum.DRIVEN
        assert result.layer == LayerEnum.ADAPTERS
        assert result.searchable_tokens == ["postgres_repo"]

    def test_short_direction_tokens(self, service):
        parts = ("adapters", "in", "api")
        boundary = self._make_boundary(parts, LayerEnum.ADAPTERS)

        result = service.define_coordinates(boundary)

        assert result.direction == DirectionEnum.DRIVING
        assert result.searchable_tokens == ["api"]

    def test_no_direction_domain_layer(self, service):
        parts = ("domain", "model", "aggregate")
        boundary = self._make_boundary(parts, LayerEnum.DOMAIN)

        result = service.define_coordinates(boundary)

        assert result.direction == DirectionEnum.UNDEFINED
        assert result.layer == LayerEnum.DOMAIN
        assert result.searchable_tokens == ["model", "aggregate"]

    def test_root_scope_layer_refinement(self, service):
        parts = ("main",)
        boundary = self._make_boundary(parts, LayerEnum.UNDEFINED, scope=ScopeEnum.ROOT)

        result = service.define_coordinates(boundary)

        assert result.layer == LayerEnum.COMPOSITION
        assert result.scope == ScopeEnum.ROOT
        assert result.searchable_tokens == ["main"]

    def test_mixed_tokens_filtering(self, service):
        parts = ("adapters", "nested", "adapters", "handler")
        boundary = self._make_boundary(parts, LayerEnum.ADAPTERS)

        result = service.define_coordinates(boundary)

        assert result.direction == DirectionEnum.UNDEFINED
        assert "adapters" not in result.searchable_tokens
        assert result.searchable_tokens == ["nested", "handler"]
