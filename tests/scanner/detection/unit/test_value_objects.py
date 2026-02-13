"""
Unit tests for Detection Value Objects: SourceFileVo and ScannedModuleVo.
"""

from pathlib import Path

from dddguard.scanner.detection.domain.value_objects import (
    ScannedModuleVo,
    SourceFileVo,
)

# ---------------------------------------------------------------------------
# SourceFileVo.is_readable
# ---------------------------------------------------------------------------


class TestSourceFileVoIsReadable:
    """Tests for the ``is_readable`` derived property."""

    def test_readable_when_content_set_and_no_error(self):
        vo = SourceFileVo(path=Path("a.py"), content="print('hello')")
        assert vo.is_readable is True

    def test_not_readable_when_content_is_none(self):
        vo = SourceFileVo(path=Path("a.py"), content=None)
        assert vo.is_readable is False

    def test_not_readable_when_reading_error_set(self):
        vo = SourceFileVo(
            path=Path("a.py"),
            content=None,
            reading_error="Binary or non-UTF8 content",
        )
        assert vo.is_readable is False

    def test_not_readable_when_content_set_but_error_also_set(self):
        """Edge case: content present but error flag raised — treated as unreadable."""
        vo = SourceFileVo(
            path=Path("a.py"),
            content="some text",
            reading_error="Unexpected partial read",
        )
        assert vo.is_readable is False

    def test_readable_with_empty_string_content(self):
        """Empty files are valid Python files (e.g. __init__.py)."""
        vo = SourceFileVo(path=Path("__init__.py"), content="")
        assert vo.is_readable is True


# ---------------------------------------------------------------------------
# ScannedModuleVo.is_package
# ---------------------------------------------------------------------------


class TestScannedModuleVoIsPackage:
    """Tests for the ``is_package`` derived property."""

    def test_is_package_for_init_file(self):
        vo = ScannedModuleVo(
            logical_path="billing.domain",
            file_path=Path("src/billing/domain/__init__.py"),
            content="",
        )
        assert vo.is_package is True

    def test_not_package_for_regular_module(self):
        vo = ScannedModuleVo(
            logical_path="billing.domain.order",
            file_path=Path("src/billing/domain/order.py"),
            content="class Order: ...",
        )
        assert vo.is_package is False

    def test_not_package_for_non_python_asset(self):
        vo = ScannedModuleVo(
            logical_path="billing.README",
            file_path=Path("src/billing/README.md"),
            content="# Billing",
        )
        assert vo.is_package is False

    def test_not_package_for_conftest(self):
        vo = ScannedModuleVo(
            logical_path="tests.conftest",
            file_path=Path("tests/conftest.py"),
            content="",
        )
        assert vo.is_package is False
