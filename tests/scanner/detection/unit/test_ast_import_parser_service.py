from pathlib import Path
from textwrap import dedent

import pytest

from dddguard.scanner.detection.domain.ast_import_parser_service import (
    AstImportParserService,
)
from dddguard.scanner.detection.domain.errors import ImportParsingError


class TestAstImportParserService:
    @pytest.fixture
    def parser(self) -> AstImportParserService:
        return AstImportParserService

    # --- 1. Absolute Imports ---

    def test_parse_simple_absolute(self, parser):
        code = dedent("""
            import os
            import numpy as np
            import my.lib.utils
        """)
        imports = parser.parse_imports(code, Path("dummy.py"), "dummy")

        assert len(imports) == 3
        # import os
        assert imports[0].module_path == "os"
        assert imports[0].imported_names == ()

        # import numpy as np (we track the source module, alias is irrelevant for graph)
        assert imports[1].module_path == "numpy"

        # import my.lib.utils
        assert imports[2].module_path == "my.lib.utils"

    def test_parse_from_absolute(self, parser):
        code = dedent("""
            from django.conf import settings
            from typing import List, Optional as Opt
        """)
        imports = parser.parse_imports(code, Path("dummy.py"), "dummy")

        assert len(imports) == 2
        # from django.conf ...
        assert imports[0].module_path == "django.conf"
        assert imports[0].imported_names == ("settings",)

        # from typing ...
        assert imports[1].module_path == "typing"
        assert set(imports[1].imported_names) == {"List", "Optional"}

    # --- 2. Relative Imports: Standard File Context ---

    def test_relative_in_standard_module(self, parser):
        """
        Context: File `src/features/login.py` (logical: `src.features.login`).
        """
        code = dedent("""
            from . import other_file       # Level 1
            from .sub import helper        # Level 1 + module
            from ..shared import config    # Level 2
        """)
        path = Path("src/features/login.py")
        logical = "src.features.login"

        imports = parser.parse_imports(code, path, logical)

        # Logic for 'login.py':
        # Base list: ['src', 'features', 'login']

        # 1. from . -> level=1. remove 'login'. Base='src.features'.
        # Target = 'src.features' (because node.module is None, but names has 'other_file')
        # Wait, strictly speaking:
        # 'from . import x' -> node.module=None. target_module=base_module.
        # VO: module="src.features", names=["other_file"]
        # Dependency is on the PACKAGE 'src.features'.
        assert imports[0].module_path == "src.features"
        assert imports[0].imported_names == ("other_file",)

        # 2. from .sub -> level=1. remove 'login'. Base='src.features'.
        # node.module='sub'. Target = 'src.features.sub'.
        assert imports[1].module_path == "src.features.sub"
        assert imports[1].imported_names == ("helper",)

        # 3. from ..shared -> level=2. remove 'login', 'features'. Base='src'.
        # node.module='shared'. Target = 'src.shared'.
        assert imports[2].module_path == "src.shared"
        assert imports[2].imported_names == ("config",)

    # --- 3. Relative Imports: __init__ Context ---

    def test_relative_in_init_file(self, parser):
        """
        Context: File `src/features/__init__.py` (logical: `src.features`).
        This is the special edge case handled by the '.__init__' suffix logic.
        """
        code = dedent("""
            from . import handlers       # Level 1
            from .utils import date_fmt  # Level 1 + module
            from .. import main_app      # Level 2
        """)
        path = Path("src/features/__init__.py")
        logical = "src.features"

        imports = parser.parse_imports(code, path, logical)

        # Logic for '__init__.py':
        # Forced Internal Base list: ['src', 'features', '__init__']

        # 1. from . -> level=1. remove '__init__'. Base='src.features'.
        # Correctly implies importing from the package itself.
        assert imports[0].module_path == "src.features"
        assert imports[0].imported_names == ("handlers",)

        # 2. from .utils -> level=1. remove '__init__'. Base='src.features'.
        # Target = 'src.features.utils'
        assert imports[1].module_path == "src.features.utils"

        # 3. from .. -> level=2. remove '__init__', 'features'. Base='src'.
        # Target = 'src'
        assert imports[2].module_path == "src"
        assert imports[2].imported_names == ("main_app",)

    # --- 4. Edge Cases ---

    def test_syntax_error(self, parser):
        code = "import ( this is invalid"
        path = Path("bad.py")

        with pytest.raises(ImportParsingError) as exc:
            parser.parse_imports(code, path, "bad")
        assert "bad.py" in str(exc.value)

    def test_deep_relative_overflow(self, parser):
        """
        Scenario: Trying to go up more levels than exist.
        Logical: 'a.b' (depth 2). Import: 'from ... import x' (level 3).
        Expectation: Should resolve to empty string or root (depending on implementation),
        but crucially should NOT crash.
        """
        code = "from ... import ghost"
        # file a/b.py -> logical a.b -> parts [a, b]
        imports = parser.parse_imports(code, Path("a/b.py"), "a.b")

        assert len(imports) == 1
        # Code logic: if level (3) > len(parts) (2) -> base_module=""
        assert imports[0].module_path == ""
