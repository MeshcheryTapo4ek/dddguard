from dataclasses import dataclass
from pathlib import Path

from dddguard.shared.domain import CodeGraph, ScannerConfig

from ...app import ScanProjectUseCase
from ..errors import InvalidScanPathError


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionFacade:
    """
    Driving Port: Exposes detection logic to the Macro Context / CLI.

    This Facade acts as the entry point for the 'Detection' Bounded Context.
    It translates external primitive signals (paths, flags) into
    executable Application Commands.
    """

    scan_use_case: ScanProjectUseCase

    def scan_physical_project(
        self, scanner_config: ScannerConfig, target_path: Path, scan_all: bool = False
    ) -> CodeGraph:
        """
        Triggers the scanning of a physical directory.

        The scan always includes:
        - Resolving logical paths (dot-notation).
        - Loading file content.
        - Parsing AST for imports (for Python files).

        :param source_dir: The root directory to start scanning.
        :param scan_all: If True, includes non-Python files (assets, configs).
                         If False, filters strictly for .py source code.
        :return: A CodeGraph object populated with 'DETECTED' or 'LINKED' nodes.
        :raises InvalidScanPathError: If the target path does not exist.
        """
        if not target_path.exists():
            raise InvalidScanPathError(str(target_path))

        # Delegate to the Use Case (Application Layer)
        return self.scan_use_case(
            scanner_config=scanner_config,
            target_path=target_path,
            scan_all=scan_all,
        )
