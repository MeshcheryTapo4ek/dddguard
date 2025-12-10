from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from ..interfaces import ITemplateRepository, IFileSystemGateway
from ...domain import TemplateCompositor
from ..errors import ScaffolderAppError


@dataclass(frozen=True, kw_only=True, slots=True)
class CreateComponentUseCase:
    """
    App Service: Generates files from a specific template (found by category & name)
    into a target directory.
    """
    template_repo: ITemplateRepository
    fs_gateway: IFileSystemGateway
    compositor: TemplateCompositor

    def execute(self, target_root: Path, category: str, template_name: str) -> None:
        """
        Args:
            target_root: Absolute path where files should be written.
            category: The category folder name (e.g., 'contexts_base').
            template_name: The template folder name OR id.
        """
        # 1. Load All Templates
        all_templates = self.template_repo.load_all()
        
        # 2. Find the requested template
        target_template_id = None
        
        for tmpl in all_templates.values():
            if tmpl.category == category:
                if tmpl.id == template_name:
                    target_template_id = tmpl.id
                    break
        
        if not target_template_id:
             raise ScaffolderAppError(f"Template '{template_name}' not found in category '{category}'.")

        # 3. Prepare Variables
        vars: Dict[str, str] = {
            "project_name": "MyProject",
            "component_name": template_name,
            "category": category,
            "python_version": "3.12"
        }
        
        # 4. Compose
        files = self.compositor.compose(
            root_template_id=target_template_id, 
            registry=all_templates, 
            runtime_variables=vars
        )
            
        if not files:
             raise ScaffolderAppError(f"Template '{target_template_id}' resulted in no files.")

        # 5. Write to Disk
        self.fs_gateway.write_files(target_root, files)