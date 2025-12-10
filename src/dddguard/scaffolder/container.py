from dataclasses import dataclass
from pathlib import Path
import typer
from dishka import Provider, Scope, provide

from .app import (
    InitProjectUseCase, 
    CreateConfigUseCase, 
    CreateComponentUseCase,
    ListTemplatesUseCase,
    ITemplateRepository, 
    IFileSystemGateway
)
from .domain import TemplateCompositor
from .adapters.driven import DiskTemplateRepository, DiskFileSystemGateway
from .ports.driving import cli as driving_adapter


@dataclass(frozen=True, kw_only=True, slots=True)
class ScaffolderContainer:
    """Facade for Scaffolder Context."""
    init_project: InitProjectUseCase
    create_config: CreateConfigUseCase 
    create_component: CreateComponentUseCase
    list_templates: ListTemplatesUseCase

    def register_commands(self, app: typer.Typer):
        driving_adapter.register_commands(
            app, 
            self.init_project, 
            self.create_config,
            self.create_component,
            self.list_templates
        )


class ScaffolderProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_template_compositor(self) -> TemplateCompositor:
        # Now uses Jinja2 internally
        return TemplateCompositor()

    @provide
    def provide_template_repo(self) -> ITemplateRepository:
        # Point to the physical 'templates' folder relative to this file
        templates_path = Path(__file__).parent / "templates"
        return DiskTemplateRepository(templates_dir=templates_path)

    @provide
    def provide_fs_gateway(self) -> IFileSystemGateway:
        return DiskFileSystemGateway()

    @provide
    def provide_create_component_use_case(
        self, 
        repo: ITemplateRepository, 
        gateway: IFileSystemGateway,
        compositor: TemplateCompositor
    ) -> CreateComponentUseCase:
        return CreateComponentUseCase(
            template_repo=repo, 
            fs_gateway=gateway,
            compositor=compositor
        )

    @provide
    def provide_init_use_case(
        self, 
        repo: ITemplateRepository, 
        gateway: IFileSystemGateway,
        component_uc: CreateComponentUseCase,
        compositor: TemplateCompositor
    ) -> InitProjectUseCase:
        return InitProjectUseCase(
            template_repo=repo, 
            fs_gateway=gateway,
            create_component_uc=component_uc,
            compositor=compositor
        )

    @provide
    def provide_create_config_use_case(
        self, gateway: IFileSystemGateway
    ) -> CreateConfigUseCase:
        return CreateConfigUseCase(fs_gateway=gateway)

    @provide
    def provide_list_templates_use_case(
        self, repo: ITemplateRepository
    ) -> ListTemplatesUseCase:
        return ListTemplatesUseCase(template_repo=repo)

    @provide
    def provide_container(
        self, 
        init_uc: InitProjectUseCase,
        config_uc: CreateConfigUseCase,
        component_uc: CreateComponentUseCase,
        list_uc: ListTemplatesUseCase
    ) -> ScaffolderContainer:
        return ScaffolderContainer(
            init_project=init_uc,
            create_config=config_uc,
            create_component=component_uc,
            list_templates=list_uc
        )