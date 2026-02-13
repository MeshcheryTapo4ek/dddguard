"""
Integration tests for FileSystemRepository.read_file().

Uses real filesystem I/O via tmp_path — no mocks.
"""

import pytest

from dddguard.scanner.detection.ports.driven.storage.file_system_repository import (
    FileSystemRepository,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo() -> FileSystemRepository:
    return FileSystemRepository()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReadFileExistingFile:
    def test_reads_utf8_python_file(self, repo, tmp_path):
        """A standard .py file should be read successfully."""
        f = tmp_path / "module.py"
        f.write_text("class Order: ...", encoding="utf-8")

        result = repo.read_file(f)

        assert result is not None
        assert result.is_readable
        assert result.content == "class Order: ..."
        assert result.reading_error is None
        assert result.path == f

    def test_reads_empty_init_file(self, repo, tmp_path):
        f = tmp_path / "__init__.py"
        f.write_text("", encoding="utf-8")

        result = repo.read_file(f)

        assert result is not None
        assert result.is_readable
        assert result.content == ""


class TestReadFileNonExistent:
    def test_returns_none_for_missing_file(self, repo, tmp_path):
        missing = tmp_path / "does_not_exist.py"

        result = repo.read_file(missing)

        assert result is None


class TestReadFileBinaryContent:
    def test_binary_file_returns_reading_error(self, repo, tmp_path):
        """
        A binary file should NOT raise an exception.
        Instead it returns a SourceFileVo with reading_error set.
        """
        f = tmp_path / "image.bin"
        f.write_bytes(b"\x00\x01\x02\xff\xfe\xfd")

        result = repo.read_file(f)

        assert result is not None
        assert not result.is_readable
        assert result.content is None
        assert result.reading_error is not None
        assert "Binary" in result.reading_error or "UTF8" in result.reading_error


class TestReadFileUnicodeContent:
    def test_reads_file_with_unicode_content(self, repo, tmp_path):
        """Files with valid UTF-8 unicode should read fine."""
        f = tmp_path / "i18n.py"
        f.write_text('MSG = "Hello world 🌍"', encoding="utf-8")

        result = repo.read_file(f)

        assert result is not None
        assert result.is_readable
        assert "Hello world" in result.content
