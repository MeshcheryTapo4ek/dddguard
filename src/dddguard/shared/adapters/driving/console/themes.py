from typing import Dict
from InquirerPy.utils import get_style


class GuardTheme:
    """Base class defining the contract for UI themes."""

    name: str
    primary_color: str  # For Rich (e.g. "cyan", "magenta")
    inquirer_style: Dict[str, str]

    def get_style(self):
        return get_style(self.inquirer_style, style_override=False)


# --- ROOT THEME (Main Menu) ---
# Main Color: Gold/Yellow (Command Center)
ROOT_THEME = GuardTheme()
ROOT_THEME.name = "root"
ROOT_THEME.primary_color = "gold1"
ROOT_THEME.inquirer_style = {
    "questionmark": "#d7af00 bold",
    "question": "#ffffff bold",
    "input": "#d7af00",
    "pointer": "#d7af00 bold",
    "checkbox": "#d7af00 bold",
    "separator": "#505050",
    "instruction": "#505050 italic",
    "answer": "#d7af00 bold",
    "highlighted": "#d7af00 bold",
    "fuzzy_prompt": "#d7af00",
    "fuzzy_match": "#d7af00 bold",
}

# --- SCANNER THEME (Discovery / Radar) ---
SCANNER_THEME = GuardTheme()
SCANNER_THEME.name = "scanner"
SCANNER_THEME.primary_color = "cyan"
SCANNER_THEME.inquirer_style = {
    "questionmark": "#00ffff bold",
    "question": "#ffffff bold",
    "input": "#00ffff",
    "pointer": "#00ffff bold",
    "checkbox": "#00ffff bold",
    "separator": "#505050",
    "instruction": "#505050 italic",
    "answer": "#00ffff bold",
    "highlighted": "#00ffff bold",
    "fuzzy_prompt": "#00ffff",
    "fuzzy_match": "#00ffff bold",
}

# --- LINTER THEME (Validation / Strictness) ---
LINTER_THEME = GuardTheme()
LINTER_THEME.name = "linter"
LINTER_THEME.primary_color = "magenta"
LINTER_THEME.inquirer_style = {
    "questionmark": "#ff00ff bold",
    "question": "#ffffff bold",
    "input": "#ff00ff",
    "pointer": "#ff00ff bold",
    "checkbox": "#ff00ff bold",
    "separator": "#505050",
    "instruction": "#505050 italic",
    "answer": "#ff00ff bold",
    "highlighted": "#ff00ff bold",
    "fuzzy_prompt": "#ff00ff",
    "fuzzy_match": "#ff00ff bold",
}

# --- SCAFFOLDER THEME (Construction / Blueprints) ---
SCAFFOLDER_THEME = GuardTheme()
SCAFFOLDER_THEME.name = "scaffolder"
SCAFFOLDER_THEME.primary_color = "blue"
SCAFFOLDER_THEME.inquirer_style = {
    "questionmark": "#5f87ff bold",
    "question": "#ffffff bold",
    "input": "#5f87ff",
    "pointer": "#5f87ff bold",
    "checkbox": "#5f87ff bold",
    "separator": "#505050",
    "instruction": "#505050 italic",
    "answer": "#5f87ff bold",
    "highlighted": "#5f87ff bold",
    "fuzzy_prompt": "#5f87ff",
    "fuzzy_match": "#5f87ff bold",
}

# --- VISUALIZER THEME (Art / Diagrams) ---
VISUALIZER_THEME = GuardTheme()
VISUALIZER_THEME.name = "visualizer"
VISUALIZER_THEME.primary_color = "purple"
VISUALIZER_THEME.inquirer_style = {
    "questionmark": "#af00ff bold",
    "question": "#ffffff bold",
    "input": "#af00ff",
    "pointer": "#af00ff bold",
    "checkbox": "#af00ff bold",
    "separator": "#505050",
    "instruction": "#505050 italic",
    "answer": "#af00ff bold",
    "highlighted": "#af00ff bold",
    "fuzzy_prompt": "#af00ff",
    "fuzzy_match": "#af00ff bold",
}

# Default Fallback
DEFAULT_THEME = SCAFFOLDER_THEME
