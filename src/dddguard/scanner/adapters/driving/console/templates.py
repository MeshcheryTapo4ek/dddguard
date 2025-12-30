from typing import Final

DEFAULT_CONFIG_TEMPLATE: Final[str] = """
project:
  # Root directory of your source code (relative to this config or project root)
  source_dir: "src"
  
  # Directory containing tests (excluded from architecture graph)
  tests_dir: "tests"
  
  # Directory for documentation output
  docs_dir: "docs"

scanner:
  # Directories to completely exclude from scanning (performance optimization)
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
