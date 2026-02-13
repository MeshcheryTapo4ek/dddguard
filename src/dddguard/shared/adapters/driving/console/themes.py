from dataclasses import dataclass
from typing import Any

from InquirerPy.utils import get_style

from ....assets.themes_data import (
    LINTER_THEME_DATA,
    ROOT_THEME_DATA,
    SCAFFOLDER_THEME_DATA,
    SCANNER_THEME_DATA,
    VISUALIZER_THEME_DATA,
    ThemeRawData,
)


@dataclass(frozen=True, slots=True)
class GuardTheme:
    """
    Adapter Class: Wraps raw theme data with InquirerPy-specific styling logic.
    """

    name: str
    primary_color: str
    inquirer_style: dict[str, str]

    @classmethod
    def from_raw(cls, data: ThemeRawData) -> "GuardTheme":
        return cls(
            name=data.name,
            primary_color=data.primary_color,
            inquirer_style=data.inquirer_style,
        )

    def get_style(self) -> Any:
        """Returns an InquirerPy style object for prompt rendering."""
        return get_style(self.inquirer_style, style_override=False)


# --- Instantiate Themes from Data ---

ROOT_THEME = GuardTheme.from_raw(ROOT_THEME_DATA)
SCANNER_THEME = GuardTheme.from_raw(SCANNER_THEME_DATA)
LINTER_THEME = GuardTheme.from_raw(LINTER_THEME_DATA)
SCAFFOLDER_THEME = GuardTheme.from_raw(SCAFFOLDER_THEME_DATA)
VISUALIZER_THEME = GuardTheme.from_raw(VISUALIZER_THEME_DATA)

# Default Fallback
DEFAULT_THEME = SCAFFOLDER_THEME
