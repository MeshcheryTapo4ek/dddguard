from dataclasses import dataclass
from pathlib import Path
from typing import List

from dddguard.shared import ConfigVo

from ..errors import ScannerAdapterError

from ...app import ScanProjectUseCase, ScannerAppError
from ...domain import ScanResult
from ...dto.driving import ScanResponseDto


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerController:
    """
    Driving Adapter: Bridges CLI and Scanner UseCase.
    """
    use_case: ScanProjectUseCase
    config: ConfigVo

    def scan_directory(
        self, 
        path: Path | None = None,
        whitelist_contexts: List[str] | None = None,
        whitelist_layers: List[str] | None = None,
        show_root: bool = True,
        show_shared: bool = True,
        dirs_only: bool = False,
        scan_all: bool = False
    ) -> ScanResponseDto:
        """
        Orchestrates scanning and maps Domain Result to DTO.
        """
        target_path = path if path else self.config.project.absolute_source_path
        
        if not target_path.exists():
             raise FileNotFoundError(f"Path not found: {target_path}")

        try:
            # 1. Execute Application Logic (Returns Domain Entity)
            result: ScanResult = self.use_case.execute(
                target_path, 
                whitelist_contexts=whitelist_contexts,
                whitelist_layers=whitelist_layers,
                show_root=show_root,
                show_shared=show_shared,
                dirs_only=dirs_only,
                scan_all=scan_all
            )
            
            # 2. Map to DTO (Adapter Responsibility)
            hierarchical_dict = result.graph.to_hierarchical_dict()
            
            return ScanResponseDto(
                source_tree=result.source_tree,
                context_count=len(hierarchical_dict.keys()),
                file_count=len(result.graph.all_nodes),
                total_lines_of_code=0 
            )

        except ScannerAppError as e:
            raise ScannerAdapterError(e.message) from e