from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from ..interfaces import ITemplateRepository, IFileSystemGateway
from ..errors import InitializationError
from ...domain import RenderedFileVo, TemplateCompositor
from ...adapters.assets import DEFAULT_CONFIG_TEMPLATE
# Correct import of the sibling use case
from .create_component_use_case import CreateComponentUseCase


@dataclass(frozen=True, kw_only=True, slots=True)
class InitProjectUseCase:
    """
    App Service: Orchestrates full project initialization.
    """
    template_repo: ITemplateRepository
    fs_gateway: IFileSystemGateway
    create_component_uc: CreateComponentUseCase
    compositor: TemplateCompositor

    def execute(self, target_path: Path, project_name: str = "My DDD Project") -> None:
        try:
            # 1. Render Skeleton (Project Base)
            all_templates = self.template_repo.load_all()
            root_template_id = "project_base"
            
            if root_template_id in all_templates:
                vars: Dict[str, str] = {
                    "project_name": project_name,
                    "python_version": "3.12",
                }

                files: List[RenderedFileVo] = self.compositor.compose(
                    root_template_id=root_template_id, 
                    registry=all_templates, 
                    runtime_variables=vars
                )
                self.fs_gateway.write_files(target_path, files)
            
            # 2. Config File
            absolute_root = target_path.resolve().as_posix()
            config_content = DEFAULT_CONFIG_TEMPLATE.format(root_dir=absolute_root)
            config_file = RenderedFileVo(
                relative_path=Path("docs/dddguard/config.yaml"),
                content=config_content
            )
            self.fs_gateway.write_files(target_path, [config_file])

            # 3. Create an Example Context
            try:
                self.create_component_uc.execute(
                    target_root=target_path,
                    category="contexts_base",
                    template_name="ctx_simple_base"
                )
            except Exception:
                pass

        except Exception as e:
            raise InitializationError(project_name, str(e)) from e