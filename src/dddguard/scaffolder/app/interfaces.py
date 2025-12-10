from typing import Protocol, Dict, List, Optional
from pathlib import Path
from ..domain.value_objects import TemplateDefinition, RenderedFileVo, CategoryDefinition


class ITemplateRepository(Protocol):

    def load_templates(self) -> Dict[str, TemplateDefinition]: 
        ...
        
    def load_all(self) -> Dict[str, TemplateDefinition]:
        ...

    def load_categories(self) -> Dict[str, CategoryDefinition]: 
        ...
        
    def get_template_source_path(self, template_id: str) -> Optional[Path]:
        """Returns the physical path to the template directory on disk."""
        ...


class IFileSystemGateway(Protocol):

    def write_files(self, target_root: Path, files: List[RenderedFileVo]) -> None: 
        ...
        
    def copy_directory(self, source: Path, destination: Path) -> None:
        """Recursively copies a directory."""
        ...