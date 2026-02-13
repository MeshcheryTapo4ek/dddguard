import pytest

from dddguard.scanner.detection.ports.driven.storage.file_system_repository import (
    FileSystemRepository,
)
from dddguard.shared.domain import ScannerConfig


# --- FIXTURES ---
@pytest.fixture
def scanner_config() -> ScannerConfig:
    """Returns a standard scanner configuration with default ignore rules."""
    return ScannerConfig(
        exclude_dirs={".git", "venv", "__pycache__"},
        ignore_files={".DS_Store", "conftest.py"},
        max_file_size_bytes=100,  # Small limit for testing
    )


@pytest.fixture
def repo() -> FileSystemRepository:
    return FileSystemRepository()


# --- TESTS ---


def test_read_project_standard_mode_py_only(repo, scanner_config, tmp_path):
    """
    Scenario: scan_all=False (Default).
    Expectation: Only .py files are yielded. Recursive traversal works.
    """
    # Arrange
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("import os", encoding="utf-8")
    (tmp_path / "src" / "utils.py").write_text("def foo(): pass", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Docs", encoding="utf-8")  # Should be ignored

    # Act
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=tmp_path, scan_all=False)
    )

    # Assert
    assert len(files) == 2
    filenames = {f.path.name for f in files}
    assert filenames == {"main.py", "utils.py"}
    assert all(f.content is not None for f in files)


def test_read_project_scan_all_mode(repo, scanner_config, tmp_path):
    """
    Scenario: scan_all=True.
    Expectation: All text files are yielded (md, txt, py).
    """
    # Arrange
    (tmp_path / "main.py").write_text("print(1)")
    (tmp_path / "notes.txt").write_text("todo list")
    (tmp_path / "config.json").write_text("{}")

    # Act
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=tmp_path, scan_all=True)
    )

    # Assert
    assert len(files) == 3
    filenames = {f.path.name for f in files}
    assert "notes.txt" in filenames
    assert "config.json" in filenames


def test_ignore_rules_dirs_and_files(repo, scanner_config, tmp_path):
    """
    Scenario: Directory structure contains excluded folders (.git) and ignored files.
    Expectation: They are skipped entirely.
    """
    # Arrange
    # 1. Valid file
    (tmp_path / "valid.py").write_text("ok")

    # 2. Ignored Dir
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("secret")

    # 3. Ignored File (defined in fixture config)
    (tmp_path / "conftest.py").write_text("ignored")

    # Act
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=tmp_path, scan_all=True)
    )

    # Assert
    assert len(files) == 1
    assert files[0].path.name == "valid.py"


def test_binary_content_yields_error_vo(repo, scanner_config, tmp_path):
    """
    Scenario: A file has .py extension but contains binary garbage (invalid UTF-8).
    Expectation: Repository does NOT raise UnicodeDecodeError.
                 It returns a SourceFileVo with .reading_error set.
    """
    # Arrange
    bad_file = tmp_path / "corrupted.py"
    # Write random binary bytes that are not valid UTF-8
    bad_file.write_bytes(b"\x80\x81\xff\xfe")

    # Act
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=tmp_path, scan_all=False)
    )

    # Assert
    assert len(files) == 1
    vo = files[0]
    assert vo.path.name == "corrupted.py"
    assert vo.content is None
    assert vo.reading_error is not None
    assert "Binary or non-UTF8" in vo.reading_error


def test_single_file_force_scan(repo, scanner_config, tmp_path):
    """
    Scenario: User points directly to a file (not a dir).
    Expectation: It is scanned even if it doesn't match filters (logic in code).
    """
    # Arrange
    target = tmp_path / "script.sh"  # usually ignored by .py filter
    target.write_text("echo hello")

    # Act
    # We pass the file path directly, not the directory
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=target, scan_all=False)
    )

    # Assert
    assert len(files) == 1
    assert files[0].path.name == "script.sh"
    assert files[0].content == "echo hello"


def test_large_file_size_limit(repo, scanner_config, tmp_path):
    """
    Scenario: File exceeds max_file_size_bytes configured in fixture (100 bytes).
    Note: The Logic in code says:
          if size > max and suffix != ".py": continue
          This means large .py files ARE allowed, but large .txt are skipped.
    """
    # Arrange
    large_content = "a" * 101  # 101 bytes

    # Case A: Large .txt (Should be SKIPPED)
    (tmp_path / "big_data.txt").write_text(large_content)

    # Case B: Large .py (Should be KEPT per current logic)
    (tmp_path / "big_code.py").write_text(large_content)

    # Act
    files = list(
        repo.read_project(scanner_config=scanner_config, target_path=tmp_path, scan_all=True)
    )

    # Assert
    filenames = {f.path.name for f in files}
    assert "big_data.txt" not in filenames
    assert "big_code.py" in filenames


def test_get_subdirectories(repo, scanner_config, tmp_path):
    """
    Scenario: Listing subfolders.
    Expectation: .git and .venv are hidden, regular folders shown.
    """
    # Arrange
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".git").mkdir()  # Should be ignored (starts with .)
    (tmp_path / "venv").mkdir()  # Should be ignored (in exclude list)

    # Act
    subdirs = repo.get_subdirectories(tmp_path, scanner_config=scanner_config)

    # Assert
    names = [p.name for p in subdirs]
    assert "src" in names
    assert "tests" in names
    assert ".git" not in names
    assert "venv" not in names
