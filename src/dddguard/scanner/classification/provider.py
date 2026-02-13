from dishka import Provider, Scope, provide

from .app import ClassifyGraphWorkflow, IdentifyComponentUseCase
from .ports.driving.facade import ClassificationFacade


class ClassificationProvider(Provider):
    """
    DI Provider for the Classification Bounded Context.
    Wires Domain Services (Stages), UseCases, and Facades.
    """

    scope = Scope.APP

    # Use Cases
    identify_uc = provide(IdentifyComponentUseCase)
    graph_workflow = provide(ClassifyGraphWorkflow)

    # Facade
    facade = provide(ClassificationFacade)
