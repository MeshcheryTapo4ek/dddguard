from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Optional, Any, List, Set

from dddguard.shared import ProjectBoundedContextNames

from ...domain import (
    ClassificationResultVo,
    AstImportParserService,
    DependencyGraph,
    DependencyNode,
    DependencyLink,
    ScanResult,
    ImportedModuleVo,
    ScannerDomainError,
)
from ..interfaces import IProjectReader
from ..errors import ProjectScanError, ScannerAppError
from .classify_file_use_case import ClassifyFileUseCase


@dataclass
class ScanProjectUseCase:
    project_reader: IProjectReader
    classifier: ClassifyFileUseCase
    parser: AstImportParserService

    def execute(
        self, 
        root_path: Path, 
        whitelist_contexts: List[str] | None = None,
        whitelist_layers: List[str] | None = None,
        show_root: bool = True,
        show_shared: bool = True,
        dirs_only: bool = False,
        scan_all: bool = False
    ) -> ScanResult:
        """
        Scans project with strict filtering by Context, Layer, and Scope (Root/Shared).
        """
        registry: Dict[str, Dict] = {}
        source_tree: Dict[str, Any] = {}
        
        allowed_contexts = set(whitelist_contexts) if whitelist_contexts else None
        allowed_layers = set(whitelist_layers) if whitelist_layers else None

        try:
            # --- Pass 1: Discovery & Indexing ---
            for source_file in self.project_reader.read_project(root_path, scan_all=scan_all):
                
                # 1. Classify
                classification = self.classifier.execute(source_file.path, root_path)
                
                # --- STRICT FILTERING START ---

                # A. Scope Filter (Root / Shared)
                if classification.scope == ProjectBoundedContextNames.COMPOSITION_ROOT and not show_root:
                    continue
                
                if classification.scope == ProjectBoundedContextNames.SHARED and not show_shared:
                    continue

                # B. Context Filter
                if allowed_contexts and classification.context_name not in allowed_contexts:
                    continue

                # C. Layer Filter
                if allowed_layers:
                    layer_val = self._get_layer_value(classification.layer)
                    if layer_val not in allowed_layers:
                        continue
                # --- STRICT FILTERING END ---

                # 2. Add to Tree
                self._add_to_tree(
                     source_tree, 
                     source_file.path, 
                     root_path, 
                     source_file.content,
                     dirs_only=dirs_only
                )
                
                # 3. Parse imports (Python Only)
                raw_imports = []
                if source_file.path.suffix == ".py":
                    try:
                        raw_imports = self.parser.parse_imports(
                            source_file.content, source_file.path, root_path
                        )
                    except ScannerDomainError as e:
                        print(f"WARN: Skipping parsing {source_file.path.name}: {e}")

                module_path = self._calculate_module_path(source_file.path, root_path)
                if not module_path:
                    continue

                is_package = source_file.path.name == "__init__.py"

                registry[module_path] = {
                    "classification": classification,
                    "raw_imports": raw_imports,
                    "is_package": is_package,
                    "file_path": source_file.path 
                }

            # --- Pass 2: Graph Construction ---
            graph = self._build_graph(registry)
            
            return ScanResult(graph=graph, source_tree=source_tree)

        except ScannerDomainError as de:
            raise ProjectScanError(root_path=str(root_path), details=str(de)) from de
        except Exception as e:
            raise ProjectScanError(root_path=str(root_path), details=str(e)) from e

    # ... (Rest of private methods: _build_graph, _add_to_tree, etc. remain unchanged)
    
    def _build_graph(self, registry: Dict[str, Dict]) -> DependencyGraph:
        # (Same implementation as previous response)
        nodes = {}
        for mod_path, data in registry.items():
            if data["is_package"]: continue 
            cls: ClassificationResultVo = data["classification"]
            node = DependencyNode(
                module_path=mod_path,
                context=cls.context_name,
                layer=cls.layer,
                component_type=cls.component_type,
                scope=cls.scope,
                imports=[] 
            )
            nodes[mod_path] = node

        for mod_path, node in list(nodes.items()):
            raw_data = registry.get(mod_path)
            if not raw_data: continue
            
            resolved_links = []
            for imp in raw_data["raw_imports"]:
                imp: ImportedModuleVo 
                names_to_resolve = imp.imported_names if imp.imported_names else [None]
                
                for imported_name in names_to_resolve:
                    target_path = imp.module_path
                    target_data = registry.get(target_path)
                    real_target_path = target_path

                    if target_data:
                        if target_data["is_package"] and imported_name:
                            re_export_path = self._find_reexport_in_package(target_data, imported_name)
                            if re_export_path:
                                real_target_path = self._resolve_relative_inside_init(target_path, re_export_path)
                    
                    final_node_data = registry.get(real_target_path)
                    if final_node_data:
                        tgt_cls = final_node_data["classification"]
                        if real_target_path == mod_path: continue
                        
                        link = DependencyLink(
                            source_module=mod_path,
                            target_module=real_target_path,
                            target_context=tgt_cls.context_name,
                            target_layer=self._get_layer_value(tgt_cls.layer),
                            target_type=self._enum_to_str(tgt_cls.component_type)
                        )
                        resolved_links.append(link)
            
            unique_links = {l.target_module: l for l in resolved_links}
            if unique_links:
                nodes[mod_path] = replace(node, imports=list(unique_links.values()))

        return DependencyGraph(nodes=nodes)

    def _find_reexport_in_package(self, package_data: Dict, name: str) -> Optional[str]:
        imports: List[ImportedModuleVo] = package_data["raw_imports"]
        for imp in imports:
            if name in imp.imported_names:
                return imp.module_path
        return None

    def _resolve_relative_inside_init(self, package_path: str, import_path: str) -> str:
        if not import_path.startswith("."):
            return import_path
        return f"{package_path}{import_path}"

    def _calculate_module_path(self, file_path: Path, root_path: Path) -> Optional[str]:
        try:
            rel_path = file_path.relative_to(root_path)
            parts = list(rel_path.with_suffix("").parts)
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]
            return ".".join(parts)
        except ValueError:
            return None

    def _add_to_tree(
        self, 
        tree: Dict, 
        file_path: Path, 
        root_path: Path, 
        content: str, 
        dirs_only: bool
    ):
        try:
            rel_path = file_path.relative_to(root_path)
        except ValueError:
            return
        parts = rel_path.parts
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = "<Some Content>" if dirs_only else content

    def _get_layer_value(self, layer_enum) -> str:
        return layer_enum.value if hasattr(layer_enum, "value") else str(layer_enum)

    def _enum_to_str(self, enum_val) -> str:
        if hasattr(enum_val, "value"): return enum_val.value
        return str(enum_val)