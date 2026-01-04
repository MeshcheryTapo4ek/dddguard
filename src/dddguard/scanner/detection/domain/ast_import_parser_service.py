import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .value_objects import ImportedModuleVo
from .errors import ImportParsingError


@dataclass(frozen=True, kw_only=True, slots=True)
class AstImportParserService:
    """
    Domain Service: Parses Python source code to extract import statements.
    Refactored to use ast.walk for conciseness.
    """

    def parse_imports(
        self,
        file_content: str,
        file_path: Path,
        logical_module_path: str,
    ) -> List[ImportedModuleVo]:
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            # Pass original error for chaining in the generic exception
            raise ImportParsingError(str(file_path), original_error=e) from e

        # Determine parsing context for relative imports
        # e.g. "pkg.mod" vs "pkg.__init__"
        current_module = logical_module_path
        if file_path.name == "__init__.py":
            current_module = f"{logical_module_path}.__init__"

        imports: List[ImportedModuleVo] = []

        for node in ast.walk(tree):
            # 1. Handle "import x, y as z"
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportedModuleVo(
                            module_path=alias.name,
                            lineno=node.lineno,
                            is_relative=False,
                            imported_names=[],
                        )
                    )

            # 2. Handle "from .x import y"
            elif isinstance(node, ast.ImportFrom):
                target_module = ""
                
                # Resolve Relative Import Logic
                if node.level > 0:
                    parts = current_module.split(".")
                    # Slice off the last 'node.level' parts to go up
                    # e.g. level=1 goes to parent
                    if node.level <= len(parts):
                        base_module = ".".join(parts[:-node.level])
                    else:
                        base_module = ""
                    
                    if node.module:
                        target_module = f"{base_module}.{node.module}" if base_module else node.module
                    else:
                        target_module = base_module
                else:
                    target_module = node.module or ""

                names_list = [alias.name for alias in node.names]

                imports.append(
                    ImportedModuleVo(
                        module_path=target_module,
                        lineno=node.lineno,
                        is_relative=node.level > 0,
                        imported_names=names_list,
                    )
                )

        return imports