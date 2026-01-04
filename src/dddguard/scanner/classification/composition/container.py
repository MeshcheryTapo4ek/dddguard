from dishka import Provider, Scope, provide

from ..domain import SrmEngineService
from ..app import ClassifyArchitectureUseCase
from ..ports.driving import ClassificationController


class ClassificationProvider(Provider):
    """
    DI Provider for the Classification Bounded Context.
    Uses auto-wiring to reduce boilerplate.
    """
    
    scope = Scope.APP

    srm_engine = provide(SrmEngineService)
    classify_use_case = provide(ClassifyArchitectureUseCase)
    controller = provide(ClassificationController)