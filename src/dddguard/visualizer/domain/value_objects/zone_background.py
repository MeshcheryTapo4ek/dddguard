from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, slots=True)
class ZoneBackground:
    """
    Value Object: Colored background rect for a Zone.
    """

    x_rel: float
    y_rel: float
    width: float
    height: float
    color: str
    side: str  # 'left', 'right', 'center'
    label: str | None = None
