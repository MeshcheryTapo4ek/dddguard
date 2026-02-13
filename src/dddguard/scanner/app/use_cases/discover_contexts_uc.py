from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import ScannerConfig

from ...domain import DiscoveredContextVo
from ..interfaces import IClassificationGateway, IDetectionGateway


@dataclass(frozen=True, kw_only=True, slots=True)
class DiscoverContextsUseCase:
    """
    Macro UseCase: Bounded Context Discovery (Inventory).

    Scans the entire project to compile a high-level list of all available Bounded Contexts.
    Used primarily by the UI/CLI Wizard to populate auto-complete lists.

    Explicitly includes SHARED and ROOT scopes as discoverable contexts.
    """

    detection_gateway: IDetectionGateway
    classification_gateway: IClassificationGateway

    def __call__(
        self,
        scanner_config: ScannerConfig,
        source_dir: Path,
        scan_all: bool = False,
    ) -> list[DiscoveredContextVo]:
        """
        Executes the discovery.

        :param scanner_config: Configuration for the scanning process.
        :param source_dir:
            Absolute path to the project source root. This is where we scan.
        :param scan_all:
            If True, includes non-Python files in the scan.
        """
        # 1. DETECT (Physical Scan)
        detected_graph = self.detection_gateway.scan(
            scanner_config=scanner_config,
            target_path=source_dir,
            scan_all=scan_all,
        )

        # 2. CLASSIFY
        classified_graph = self.classification_gateway.classify(
            graph=detected_graph, source_dir=source_dir
        )

        # 3. AGGREGATE & DEDUPLICATE
        unique_contexts: dict[tuple[str, str | None], DiscoveredContextVo] = {}

        for node in classified_graph.nodes.values():
            passport = node.passport

            if not passport or not passport.context_name:
                continue

            key = (passport.context_name, passport.macro_zone)

            if key not in unique_contexts:
                unique_contexts[key] = DiscoveredContextVo(
                    context_name=passport.context_name,
                    macro_zone=passport.macro_zone,
                )

        # 4. SORT
        def sort_key(c: DiscoveredContextVo):
            if c.context_name == "root":
                return ("0_root", "")
            if c.context_name == "shared":
                return ("1_shared", "")
            return ("2_biz", c.macro_zone or "", c.context_name)

        return sorted(unique_contexts.values(), key=sort_key)
