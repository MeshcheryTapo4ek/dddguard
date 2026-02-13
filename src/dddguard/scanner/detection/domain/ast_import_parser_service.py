import ast
from dataclasses import dataclass
from pathlib import Path

from .errors import ImportParsingError
from .value_objects import ImportedModuleVo


@dataclass(frozen=True, kw_only=True, slots=True)
class AstImportParserService:
    """
    Domain Service: Static Analysis of Python Source Code.

    Responsibility:
    Parses a single file's content (AST) to extract import statements.

    Principles:
    1. Isolated/Blind: It does NOT check the file system. It does not know if imported modules exist.
    2. Syntax-Driven: It trusts the Python syntax. 'from . import x' is parsed purely via string manipulation
       of the logical path, assuming standard Python import resolution rules.
    """

    @staticmethod
    def parse_imports(
        file_content: str,
        file_path: Path,
        logical_module_path: str,
    ) -> list[ImportedModuleVo]:
        """
        Extracts dependencies from Python source code.

        :param file_content: The raw string content of the file.
        :param file_path: Physical path (used only for error context and __init__ detection).
        :param logical_module_path: The calculated dot-notation path (e.g. 'app.services.auth').
                                    CRITICAL for resolving relative imports correctly.
        :return: List of imported modules.
        :raises ImportParsingError: If AST parsing fails (SyntaxError).
        """
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            # Pass original error for chaining in the generic exception
            raise ImportParsingError(str(file_path), original_error=e) from e

        # Determine parsing context for relative imports.
        # Logic:
        # - "Standard Module" (foo.py): logical="pkg.foo". "from ." (level 1) means we look in "pkg".
        #   Math: "pkg.foo".split()[:-1] -> "pkg".
        # - "Init Module" (__init__.py): logical="pkg". "from ." (level 1) means we look in "pkg" (itself).
        #   Problem: "pkg".split()[:-1] -> "". (Wrong).
        #   Fix: We temporarily treat it as "pkg.__init__".
        #   Math: "pkg.__init__".split()[:-1] -> "pkg". (Correct).
        current_module = logical_module_path
        if file_path.name == "__init__.py":
            current_module = f"{logical_module_path}.__init__"

        imports: list[ImportedModuleVo] = []

        for node in ast.walk(tree):
            # 1. Handle "import x, y as z"
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportedModuleVo(
                            module_path=alias.name,
                            lineno=node.lineno,
                            is_relative=False,
                            imported_names=(),
                        )
                    )

            # 2. Handle "from .x import y"
            elif isinstance(node, ast.ImportFrom):
                target_module = ""

                # Resolve Relative Import Logic
                if node.level > 0:
                    parts = current_module.split(".")
                    # Slice off the last 'node.level' parts to go up
                    # e.g. level=1 goes to parent directory of the *file*
                    if node.level <= len(parts):
                        base_module = ".".join(parts[: -node.level])
                    else:
                        base_module = ""

                    if node.module:
                        target_module = (
                            f"{base_module}.{node.module}" if base_module else node.module
                        )
                    else:
                        target_module = base_module
                else:
                    # Absolute 'from x import y'
                    target_module = node.module or ""

                imported_names = tuple(alias.name for alias in node.names)

                imports.append(
                    ImportedModuleVo(
                        module_path=target_module,
                        lineno=node.lineno,
                        is_relative=node.level > 0,
                        imported_names=imported_names,
                    )
                )

        return imports
