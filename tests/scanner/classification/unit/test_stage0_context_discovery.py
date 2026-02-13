import pytest

from dddguard.scanner.classification.domain.services.stage0_context_discovery import (
    Stage0ContextDiscoveryService,
)
from dddguard.shared.domain import LayerEnum, ScopeEnum


class TestStage0ContextDiscoveryService:
    @pytest.fixture
    def service(self):
        return Stage0ContextDiscoveryService

    def test_discovery_standard_leaf_context(self, service):
        parts = ("src", "logistics", "fleet", "domain", "vehicle")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.scope == ScopeEnum.CONTEXT
        assert result.context_name == "fleet"
        assert result.macro_path == "logistics"
        assert result.detected_layer_token == LayerEnum.DOMAIN

    def test_discovery_root_scope(self, service):
        parts = ("src", "composition", "container")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.scope == ScopeEnum.ROOT
        assert result.context_name == "root"
        assert result.detected_layer_token == LayerEnum.COMPOSITION

    def test_discovery_shared_kernel(self, service):
        parts = ("src", "shared", "domain", "vo")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.scope == ScopeEnum.SHARED
        assert result.context_name == "shared"
        assert result.detected_layer_token == LayerEnum.DOMAIN

    def test_inference_from_filename(self, service):
        parts = ("src", "billing", "facade")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.context_name == "billing"
        assert result.detected_layer_token == LayerEnum.PORTS

    def test_discovery_deep_macro_zone(self, service):
        parts = ("src", "org", "dept", "team", "project", "app", "service")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.context_name == "project"
        assert result.macro_path == "org/dept/team"
        assert result.detected_layer_token == LayerEnum.APP

    def test_fallback_to_generic_context(self, service):
        parts = ("src", "mystery_box", "random_file")

        result = service.detect_context_boundary(source_dir="src", relative_path_parts=parts)

        assert result.detected_layer_token == LayerEnum.UNDEFINED
        assert result.context_name == "mystery_box"
