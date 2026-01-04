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
    PathFilter,
    ImportParsingError  # Explicitly import the domain error
)
from ..interfaces import IProjectReader
from ..errors import ProjectScanError


@dataclass(frozen=True, kw_only=True, slots=True)
class ScanProjectUseCase:
    """
    App Service:
    1. Reads files.
    2. Resolves python paths.
    3. Parses imports.
    4. Builds raw graph.
    """

    project_reader: IProjectReader
    parser: AstImportParserService
    module_resolver: ModuleResolutionService
    dependency_service: DependencyExpansionService

    def execute(
        self,
        scan_root: Path,
        focus_path: Path,
        dirs_only: bool = False,
        scan_all: bool = False,
        import_depth: int = 0,
        include_paths: List[Path] | None = None,
    ) -> ScanResult:
        registry: Dict[str, ScannedModuleVo] = {}

        try:
            # 1. Ingest
            for source_file in self.project_reader.read_project(
                scan_root, scan_all=scan_all
            ):
                self._ingest_file(source_file, scan_root, registry)

            # 2. Build Raw Graph
            graph = self._build_raw_graph(registry, scan_root)

            # 3. Apply Physical Filters (Using new PathFilter VO)
            path_filter = PathFilter(
                focus_path=focus_path, 
                include_paths=include_paths
            )
            
            self.dependency_service.apply_path_filters(
                graph=graph,
                registry=registry,
                path_filter=path_filter,
            )

            # 4. Expand by Imports (BFS)
            if import_depth > 0:
                self.dependency_service.expand_by_imports(
                    graph=graph,
                    registry=registry,
                    initial_budget=import_depth,
                )

            # 5. Build Tree Presentation
            project_tree = ProjectStructureTree()
            for node in graph.visible_nodes:
                module_vo = registry.get(node.module_path)
                if module_vo:
                    project_tree.add_module(module_vo, scan_root, dirs_only)

            return ScanResult(
                graph=graph, 
                source_tree=project_tree.to_dict(),
                stats=graph.compute_statistics()
            )

        except Exception as e:
            # Top-level catch-all for critical failures (e.g. MemoryError, Disk Failure)
            raise ProjectScanError(
                root_path=str(focus_path), 
                details=str(e),
                original_error=e
            ) from e

    def _ingest_file(
        self,
        source_file,
        project_root: Path,
        registry: Dict[str, ScannedModuleVo],
    ) -> None:
        logical_path = self.module_resolver.calculate_logical_path(
            source_file.path, project_root
        )
        if not logical_path:
            return

        raw_imports = []
        
        # --- RESILIENCE UPDATE START ---
        # Handle syntax errors gracefully per file so one bad file doesn't kill the scan
        if source_file.path.suffix == ".py":
            try:
                raw_imports = self.parser.parse_imports(
                    source_file.content, source_file.path, logical_path
                )
            except ImportParsingError:
                # We simply ignore parsing errors for this file.
                # It will be registered as a module with 0 imports.
                pass
        # --- RESILIENCE UPDATE END ---

        module_vo = ScannedModuleVo(
            logical_path=logical_path,
            file_path=source_file.path,
            content=source_file.content,
            raw_imports=raw_imports,
        )
        registry[logical_path] = module_vo

    def _build_raw_graph(self, registry: Dict[str, ScannedModuleVo], scan_root: Path) -> DependencyGraph:
        graph = DependencyGraph()
        
        # Create Nodes
        for mod_path in registry.keys():
            graph.add_node(DependencyNode(module_path=mod_path))

        root_dir_name = scan_root.name 

        # Link Nodes
        for node in graph.all_nodes:
            module_vo = registry.get(node.module_path)
            if not module_vo:
                continue

            resolved_links = []
            for imp in module_vo.raw_imports:
                target_path = imp.module_path
                target_vo = registry.get(target_path)
                
                # Resolve relative/aliased paths
                if not target_vo:
                    normalized = self._normalize_import_path(target_path, root_dir_name)
                    if normalized and normalized in registry:
                        target_path = normalized
                        target_vo = registry.get(target_path)

                if target_vo:
                    resolved_links.append(
                        DependencyLink(
                            source_module=node.module_path,
                            target_module=target_path,
                            imported_symbols=imp.imported_names
                        )
                    )
            
            node.imports = resolved_links

        return graph

    def _normalize_import_path(self, import_path: str, root_dir_name: str) -> str | None:
        parts = import_path.split(".")
        if not parts:
            return None
        if parts[0] == root_dir_name:
            return ".".join(parts[1:])
        return None