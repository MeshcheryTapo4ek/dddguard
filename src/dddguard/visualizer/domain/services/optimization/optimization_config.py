from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class OptimizationConfig:
    """
    Configuration for container layout optimization.
    """

    max_children_guard: int = 28
    iterations: int = 1000
    restarts: int = 100

    lambda_y: float = 1.0
    shape_penalty: float = 0.02
    
    upward_penalty: float = 2.0  # Cost multiplier for upward arrows
    external_attraction: float = 1.5 # Weight for external anchors

    # Accept only improvements (deterministic hill-climb).
    allow_worse_moves: bool = False