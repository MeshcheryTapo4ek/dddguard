from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from ...domain import (
    AstImportParserService,
    DependencyGraph,
    DependencyNode,
    DependencyLink,
    ScanResult,
    ModuleResolutionService,
    DependencyExpansionService,
    ScannedModuleVo,
    ProjectStructureTree,
)
from ..interfaces import IProjectReader
from ..errors import ProjectScanError
from .classify_file_use_case import ClassifyFileUseCase


@dataclass(frozen=True, kw_only=True, slots=True)
class ScanProjectUseCase:
    """
    App Service:
    Orchestrates the ingestion, graph building, and expansion via Domain Services.
    """

    project_reader: IProjectReader
    classifier: ClassifyFileUseCase
    parser: AstImportParserService
    module_resolver: ModuleResolutionService
    dependency_service: DependencyExpansionService

    def execute(
        self,
        scan_root: Path,
        focus_path: Path,
        whitelist_contexts: List[str] | None = None,
        whitelist_layers: List[str] | None = None,
        dirs_only: bool = False,
        scan_all: bool = False,
        import_depth: int = 0,
    ) -> ScanResult:
        registry: Dict[str, ScannedModuleVo] = {}

        try:
            # === PHASE 1: INGEST EVERYTHING (Full Project) ===
            for source_file in self.project_reader.read_project(
                scan_root, scan_all=scan_all
            ):
                self._ingest_file(
                    source_file=source_file,
                    project_root=scan_root,
                    registry=registry,
                )

            # Build the Full Graph (Nodes & Edges)
            graph = self._build_initial_graph(registry, scan_root)

            # === PHASE 2: APPLY FILTERS (Domain Logic) ===
            self.dependency_service.apply_visibility_filters(
                graph=graph,
                registry=registry,
                focus_path=str(focus_path),
                whitelist_contexts=set(whitelist_contexts) if whitelist_contexts else None,
                whitelist_layers=set(whitelist_layers) if whitelist_layers else None,
            )

            # === PHASE 3: EXPAND DEPENDENCIES (Domain Logic) ===
            if import_depth > 0:
                self.dependency_service.expand_visibility_by_imports(
                    graph=graph,
                    registry=registry,
                    initial_budget=import_depth,
                )

            # === PHASE 4: CONSTRUCT VISIBLE TREE ===
            project_tree = ProjectStructureTree()
            
            for node in graph.visible_nodes:
                module_vo = registry.get(node.module_path)
                if module_vo:
                    project_tree.add_module(module_vo, scan_root, dirs_only)
            
            return ScanResult(graph=graph, source_tree=project_tree.to_dict())

        except Exception as e:
            raise ProjectScanError(root_path=str(focus_path), details=str(e)) from e

    def _ingest_file(
        self,
        source_file,
        project_root: Path,
        registry: Dict[str, ScannedModuleVo],
    ) -> None:
        classification = self.classifier.execute(source_file.path, project_root)

        logical_path = self.module_resolver.calculate_logical_path(
            source_file.path, project_root
        )
        if not logical_path:
            return

        raw_imports = []
        if source_file.path.suffix == ".py":
            raw_imports = self.parser.parse_imports(
                source_file.content, source_file.path, logical_path
            )

        module_vo = ScannedModuleVo(
            logical_path=logical_path,
            file_path=source_file.path,
            content=source_file.content,
            classification=classification,
            raw_imports=raw_imports,
        )
        registry[logical_path] = module_vo

    def _build_initial_graph(self, registry: Dict[str, ScannedModuleVo], scan_root: Path) -> DependencyGraph:
        graph = DependencyGraph()
        for mod_path, module_vo in registry.items():
            cls = module_vo.classification
            node = DependencyNode(
                module_path=mod_path,
                context=cls.context_name,
                layer=cls.layer,
                component_type=cls.component_type,
                scope=cls.scope,
                is_visible=False,
            )
            graph.add_node(node)

        # Link Edges with Normalization & Symbol Extraction
        root_dir_name = scan_root.name 

        for node in graph.all_nodes:
            module_vo = registry.get(node.module_path)
            if not module_vo:
                continue

            resolved_links = []
            for imp in module_vo.raw_imports:
                target_path = imp.module_path
                target_vo = registry.get(target_path)
                
                # --- PATH NORMALIZATION ---
                if not target_vo:
                    normalized = self._normalize_import_path(target_path, root_dir_name)
                    if normalized and normalized in registry:
                        target_path = normalized
                        target_vo = registry.get(target_path)
                # --------------------------

                if target_vo:
                    tgt_cls = target_vo.classification
                    resolved_links.append(
                        DependencyLink(
                            source_module=node.module_path,
                            target_module=target_path,
                            target_context=tgt_cls.context_name,
                            target_layer=str(tgt_cls.layer),
                            target_type=str(tgt_cls.component_type),
                            imported_symbols=imp.imported_names # COPY SYMBOLS
                        )
                    )
            
            # Merge duplicate links
            unique_links_map = {}
            for link in resolved_links:
                if link.target_module not in unique_links_map:
                    unique_links_map[link.target_module] = link
                else:
                    existing = unique_links_map[link.target_module]
                    merged_symbols = list(set(existing.imported_symbols + link.imported_symbols))
                    unique_links_map[link.target_module] = DependencyLink(
                        source_module=existing.source_module,
                        target_module=existing.target_module,
                        target_context=existing.target_context,
                        target_layer=existing.target_layer,
                        target_type=existing.target_type,
                        imported_symbols=merged_symbols
                    )

            node.imports = list(unique_links_map.values())

        return graph

    def _normalize_import_path(self, import_path: str, root_dir_name: str) -> str | None:
        parts = import_path.split(".")
        if not parts:
            return None
        if parts[0] == root_dir_name:
            return ".".join(parts[1:])
        return None