from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import (
    CodeGraph,
    ConfigVo,
)

from ...app import DiscoverContextsUseCase, InspectTreeUseCase, RunScanUseCase
from ...domain import DiscoveredContextVo
from ..errors import InvalidScanPathError


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextNodeSchema:
    context_name: str
    macro_zone: str | None


@dataclass(frozen=True, kw_only=True, slots=True)
class ContextListSchema:
    contexts: list[ContextNodeSchema]


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerFacade:
    """
    Driving Port: Public API of the Scanner Context.

    Responsibilities:
    1. Own the ConfigVo and extract source_dir from it.
    2. Validate that source_dir exists and is accessible.
    3. Pass source_dir to all Use Cases as the single path parameter.
    4. Coordinate between UI/CLI requirements and Application Use Cases.

    **Design Principle**: Use Cases receive only `source_dir: Path`.
    All path logic is encapsulated in the Facade.
    """

    run_scan_use_case: RunScanUseCase
    inspect_tree_use_case: InspectTreeUseCase
    discover_contexts_use_case: DiscoverContextsUseCase
    config: ConfigVo

    def scan_project(
        self,
        target_path: Path | None = None,
        whitelist_contexts: list[str] | None = None,
        whitelist_layers: list[str] | None = None,
        scan_all: bool = False,
        import_depth: int = 0,
        include_assets: bool = True,
    ) -> CodeGraph:
        """
        Runs the full scanning pipeline.

        Use `whitelist_contexts` and `whitelist_layers` to control visibility.
        """
        if not target_path:
            target_path = self._get_source_dir()

        return self.run_scan_use_case(
            scanner_config=self.config.scanner,
            source_dir=target_path,
            scan_all=scan_all,
            import_depth=import_depth,
            whitelist_layers=whitelist_layers,
            whitelist_contexts=whitelist_contexts,
            include_assets=include_assets,
        )

    def classify_tree(self, target_path: Path | None = None) -> CodeGraph:
        """
        Scans and classifies the tree, returning the CodeGraph.
        """
        if not target_path:
            target_path = self._get_source_dir()

        return self.inspect_tree_use_case(
            scanner_config=self.config.scanner,
            source_dir=target_path,
            scan_all=False,
        )

    def discover_contexts(self, target_path: Path | None = None) -> ContextListSchema:
        """
        Performs structural discovery to find all Bounded Contexts.
        """
        if not target_path:
            target_path = self._get_source_dir()

        results: list[DiscoveredContextVo] = self.discover_contexts_use_case(
            scanner_config=self.config.scanner,
            source_dir=target_path,
            scan_all=False,
        )

        return ContextListSchema(
            contexts=[
                ContextNodeSchema(context_name=c.context_name, macro_zone=c.macro_zone)
                for c in results
            ]
        )

    def _get_source_dir(self) -> Path:
        """
        Internal Helper: Extracts and validates source_dir from Config.

        This is the single point where path resolution happens.
        Throws InvalidScanPathError if config is missing or invalid.
        """
        source_dir = self.config.project.absolute_source_path

        if source_dir is None:
            raise InvalidScanPathError(
                "No 'source_dir' found in configuration. "
                "Please configure 'project.source_dir' in config.yaml."
            )

        if not source_dir.exists():
            raise InvalidScanPathError(f"Configured source directory does not exist: {source_dir}")

        if not source_dir.is_dir():
            raise InvalidScanPathError(f"Configured source path is not a directory: {source_dir}")

        return source_dir
