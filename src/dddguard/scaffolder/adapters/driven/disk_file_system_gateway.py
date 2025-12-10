import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

from ...app import IFileSystemGateway, ScaffolderAppError
from ...domain import RenderedFileVo


@dataclass(frozen=True, kw_only=True, slots=True)
class DiskFileSystemGateway(IFileSystemGateway):
    
    def write_files(self, target_root: Path, files: List[RenderedFileVo]) -> None:
        try:
            if not target_root.exists():
                target_root.mkdir(parents=True, exist_ok=True)

            for file_vo in files:
                full_path = target_root / file_vo.relative_path

                if not full_path.parent.exists():
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file_vo.content)
                    
        except Exception as e:
            raise ScaffolderAppError(f"Failed to write files: {e}")

    def copy_directory(self, source: Path, destination: Path) -> None:
        try:
            if destination.exists():
                # If it exists, we skip or merge? Logic says if template exists locally, use it.
                # Here we just copy if missing or overwrite? 
                # Let's overwrite to ensure freshness if we are explicitly 'ejecting'
                # But typically 'dirs_exist_ok=True' is good.
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copytree(source, destination)
        except Exception as e:
             raise ScaffolderAppError(f"Failed to copy directory {source} to {destination}: {e}")