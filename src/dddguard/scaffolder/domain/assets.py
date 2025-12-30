from typing import Final

DEFAULT_CONFIG_TEMPLATE: Final[str] = """
project:
  root_dir: "{root_dir}"
  source_dir: "src"
  tests_dir: "tests"
  docs_dir: "docs"

scanner:
  # Directories to completely exclude from scanning
  exclude_dirs:
    - ".git"
    - ".venv"
    - "venv"
    - "__pycache__"
    - "node_modules"
    - "migrations"
    - "build"
    - "dist"
    - ".idea"
    - ".vscode"

  # Specific files to ignore during analysis
  ignore_files:
    - "conftest.py"
    - "manage.py"
    - "setup.py"
    - "__main__.py"
""".strip()
