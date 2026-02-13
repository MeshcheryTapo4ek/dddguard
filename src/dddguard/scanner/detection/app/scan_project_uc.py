import logging
from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph, ScannerConfig
from dddguard.shared.helpers.generics import GenericAppError

from ..domain import (
    AstImportParserService,
    ImportParsingError,
    ModuleResolutionService,
    RecursiveImportResolverService,
    ScannedModuleVo,
    SourceFileVo,
)
from .interfaces import IProjectReader

logger = logging.getLogger(__name__)

# Type alias: logical_path -> scanned module
ModuleRegistry = dict[str, ScannedModuleVo]


class ProjectScanError(GenericAppError):
    """
    Critical failure executing the scanning process.
    """

    def __init__(
        self,
        root_path: str,
        details: str = "",
        original_error: Exception | None = None,
    ):
        msg = f"Failed to scan project at: {root_path}. Reason: {details}"
        super().__init__(
            message=msg, context_name="Scanner.Detection", original_error=original_error
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class ScanProjectUseCase:
    """
    App Service (Orchestrator):
    Coordinates the process of turning a physical file system into a logical CodeGraph.
    Uses stateless Domain Services for parsing and resolution.
    """

    project_reader: IProjectReader

    def __call__(
        self,
        scanner_config: ScannerConfig,
        target_path: Path,
        scan_all: bool = False,
    ) -> CodeGraph:
        """
        Executes the scanning workflow.
        """
        # Local registry to hold intermediate VOs before Graph construction
        registry: ModuleRegistry = {}

        try:
            # --- PHASE 1: INGEST ---
            for source_file in self.project_reader.read_project(
                scanner_config=scanner_config,
                target_path=target_path,
                scan_all=scan_all,
            ):
                self._ingest_file(source_file, source_dir=target_path, registry=registry)

            # --- PHASE 2: LINKING & GRAPH BUILD ---
            return self._build_graph(registry, source_dir=target_path)

        except Exception as e:
            raise ProjectScanError(
                root_path=str(target_path), details=str(e), original_error=e
            ) from e

    def _ingest_file(
        self,
        source_file: SourceFileVo,
        source_dir: Path,
        registry: ModuleRegistry,
    ) -> None:
        """
        Helper: Resolves logical path and parses raw imports (AST).
        """
        # 1. Resolve Logical Path
        logical_path = ModuleResolutionService.calculate_logical_path(source_file.path, source_dir)
        if not logical_path:
            return

        # 2. Parse AST (Only for Python files)
        raw_imports = []
        if source_file.path.suffix == ".py" and source_file.content is not None:
            try:
                raw_imports = AstImportParserService.parse_imports(
                    source_file.content, source_file.path, logical_path
                )
            except ImportParsingError as e:
                logger.warning(
                    "Skipping import parsing for %s: %s",
                    source_file.path,
                    e,
                )

        # 3. Register
        registry[logical_path] = ScannedModuleVo(
            logical_path=logical_path,
            file_path=source_file.path,
            content=source_file.content,
            raw_imports=raw_imports,
        )

    def _build_graph(self, registry: ModuleRegistry, source_dir: Path) -> CodeGraph:
        """
        Constructs the CodeGraph and transitions nodes to LINKED status.
        """
        graph = CodeGraph()
        source_dir_name = source_dir.name

        # A. Create Nodes
        for mod_path, vo in registry.items():
            graph.add_node(path=mod_path, file_path=vo.file_path, content=vo.content)

        # B. Link Nodes
        for node in graph.nodes.values():
            module_vo = registry.get(node.path)
            if not module_vo or not module_vo.raw_imports:
                continue

            final_targets: set[str] = set()

            for imp in module_vo.raw_imports:
                base_target = imp.module_path

                # 1. Resolve Specific Names (Deep Recursion)
                if imp.imported_names:
                    for name in imp.imported_names:
                        resolved = RecursiveImportResolverService.resolve(
                            registry=registry,
                            start_module_path=base_target,
                            imported_name=name,
                            source_dir_name=source_dir_name,
                        )
                        final_targets.add(resolved)

                # 2. Base Linking (Fallback for direct imports or empty names)
                else:
                    target = self._normalize_if_needed(base_target, registry, source_dir)
                    if target:
                        final_targets.add(target)

            if final_targets:
                node.link_imports(list(final_targets))

        return graph

    def _normalize_if_needed(
        self,
        target: str,
        registry: ModuleRegistry,
        source_dir: Path,
    ) -> str | None:
        """
        Tries to find the target in registry, applying normalization if needed.
        """
        if target in registry:
            return target

        # Strip source_dir prefix logic
        parts = target.split(".")
        if parts and parts[0] == source_dir.name:
            normalized = ".".join(parts[1:])
            if normalized in registry:
                return normalized

        return None
