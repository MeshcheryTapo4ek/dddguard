import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

from ...value_objects import ImportedModuleVo
from ...errors import ImportParsingError


@dataclass(frozen=True, kw_only=True, slots=True)
class AstImportParserService:
    """
    Domain Service: Parses Python source code to extract import statements.
    """

    def parse_imports(
        self, file_content: str, file_path: Path, project_root: Path
    ) -> List[ImportedModuleVo]:
        try:
            tree = ast.parse(file_content)
        except SyntaxError as e:
            # Domain logic dictates: code must be parseable.
            raise ImportParsingError(str(file_path)) from e

        # ... (rest of logic: canonical_module_path calculation, visitor usage)
        # Assuming the rest of the file logic remains the same as previously provided
        canonical_module_path = self._get_module_path(file_path, project_root)
        
        parsing_context_path = canonical_module_path
        if file_path.name == "__init__.py":
             parsing_context_path = f"{canonical_module_path}.__init__"

        visitor = _ImportVisitor(parsing_context_path)
        visitor.visit(tree)

        return visitor.imports

    def _get_module_path(self, file_path: Path, project_root: Path) -> str:
        try:
            rel_path = file_path.relative_to(project_root)
            parts = list(rel_path.parts)

            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            else:
                parts[-1] = parts[-1].replace(".py", "")

            return ".".join(parts)
        except ValueError:
            return ""

# _ImportVisitor class remains unchanged
class _ImportVisitor(ast.NodeVisitor):
    def __init__(self, current_module_path: str):
        self.current_module = current_module_path
        self.imports: List[ImportedModuleVo] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ImportedModuleVo(
                    module_path=alias.name, 
                    lineno=node.lineno, 
                    is_relative=False,
                    imported_names=[] 
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        target_module = ""

        if node.level > 0:
            parts = self.current_module.split(".")
            base_module = ".".join(parts[: -node.level]) if node.level <= len(parts) else ""
            if node.module:
                target_module = f"{base_module}.{node.module}" if base_module else node.module
            else:
                target_module = base_module
        else:
            target_module = node.module or ""
        
        names_list = [alias.name for alias in node.names]

        self.imports.append(
            ImportedModuleVo(
                module_path=target_module,
                lineno=node.lineno,
                is_relative=node.level > 0,
                imported_names=names_list
            )
        )
        self.generic_visit(node)