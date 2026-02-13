from pathlib import Path

import pytest

from dddguard.scanner.classification.app.identify_component_uc import (
    IdentifyComponentUseCase,
)
from dddguard.shared.domain import (
    AdapterType,
    AppType,
    ArchetypeType,
    ComponentPassport,
    CompositionType,
    DomainType,
    LayerEnum,
    MatchMethod,
    PortType,
    ScopeEnum,
)


class TestIdentifyComponentUseCaseFlow:
    @pytest.fixture
    def project_root(self, tmp_path):
        """
        Uses pytest's tmp_path to create a real temporary directory.
        This ensures path resolution logic works correctly without mocking properties.
        """
        return tmp_path

    @pytest.fixture
    def source_dir(self, project_root):
        """The source directory (src/) within the project root."""
        return project_root / "src"

    @pytest.fixture
    def use_case(self):
        return IdentifyComponentUseCase()

    @pytest.mark.parametrize(
        ("rel_path", "expected_layer", "expected_type", "expected_ctx"),
        [
            # --- DOMAIN LAYER ---
            (
                "src/ordering/domain/order_ent.py",
                LayerEnum.DOMAIN,
                DomainType.ENTITY,
                "ordering",
            ),
            (
                "src/ordering/domain/services/pricing_service.py",
                LayerEnum.DOMAIN,
                DomainType.DOMAIN_SERVICE,
                "ordering",
            ),
            # --- APP LAYER ---
            (
                "src/ordering/app/use_cases/create_order.py",
                LayerEnum.APP,
                AppType.USE_CASE,
                "ordering",
            ),
            # --- ADAPTERS (DRIVING) ---
            (
                "src/ordering/adapters/driving/web/order_controller.py",
                LayerEnum.ADAPTERS,
                AdapterType.CONTROLLER,
                "ordering",
            ),
            # --- ADAPTERS (DRIVEN) ---
            (
                "src/ordering/adapters/driven/postgres/order_repository.py",
                LayerEnum.ADAPTERS,
                AdapterType.REPOSITORY,
                "ordering",
            ),
            # --- PORTS ---
            (
                "src/ordering/ports/driving/payment_facade.py",
                LayerEnum.PORTS,
                PortType.FACADE,
                "ordering",
            ),
            # --- SHARED KERNEL ---
            (
                "src/shared/domain/money_vo.py",
                LayerEnum.DOMAIN,
                DomainType.VALUE_OBJECT,
                "shared",
            ),
            # --- COMPOSITION / ROOT ---
            (
                "src/composition/main.py",
                LayerEnum.COMPOSITION,
                CompositionType.ENTRYPOINT,
                "root",
            ),
            # --- MARKERS ---
            (
                "src/ordering/__init__.py",
                LayerEnum.UNDEFINED,
                ArchetypeType.MARKER,
                "ordering",
            ),
            # --- LAYER INFERENCE (Fallback) ---
            (
                "src/common/utils/string_helper.py",
                LayerEnum.GLOBAL,
                ArchetypeType.HELPER,
                "root",
            ),
        ],
    )
    def test_identify_various_components(
        self,
        use_case,
        project_root,
        source_dir,
        rel_path,
        expected_layer,
        expected_type,
        expected_ctx,
    ):
        """
        Flow Test: Verifies the entire classification pipeline.
        """
        # Create a dummy file so .resolve() and .exists() checks (if any) pass physically
        # or at least the Path object behaves correctly.
        file_path = project_root / rel_path

        # Act — source_dir is project_root/src, matching production usage
        passport: ComponentPassport = use_case(file_path, source_dir)

        # Assert
        assert passport.context_name == expected_ctx
        assert passport.layer == expected_layer, f"Failed Layer for {rel_path}"
        assert passport.component_type != ArchetypeType.UNKNOWN

        if expected_type:
            assert passport.component_type == expected_type, f"Failed Type for {rel_path}"

    def test_security_boundary_check(self, use_case, source_dir):
        """Check that files outside project root return UNKNOWN."""
        outside_path = Path("/etc/passwd")

        passport = use_case(outside_path, source_dir)

        assert passport.component_type == ArchetypeType.UNKNOWN
        assert passport.match_method == MatchMethod.UNKNOWN

    def test_shared_scope_detection(self, use_case, project_root, source_dir):
        """Verify Scope is correctly set to SHARED."""
        path = project_root / "src/shared/domain/money.py"

        passport = use_case(path, source_dir)

        assert passport.scope == ScopeEnum.SHARED
