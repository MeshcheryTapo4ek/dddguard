from typing import NamedTuple


class ThemeRawData(NamedTuple):
    name: str
    primary_color: str
    inquirer_style: dict[str, str]


# --- ROOT THEME (Main Menu) ---
ROOT_THEME_DATA = ThemeRawData(
    name="root",
    primary_color="gold1",
    inquirer_style={
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
    },
)

# --- SCANNER THEME (Discovery / Radar) ---
SCANNER_THEME_DATA = ThemeRawData(
    name="scanner",
    primary_color="cyan",
    inquirer_style={
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
    },
)

# --- LINTER THEME (Validation / Strictness) ---
LINTER_THEME_DATA = ThemeRawData(
    name="linter",
    primary_color="magenta",
    inquirer_style={
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
    },
)

# --- SCAFFOLDER THEME (Construction / Blueprints) ---
SCAFFOLDER_THEME_DATA = ThemeRawData(
    name="scaffolder",
    primary_color="blue",
    inquirer_style={
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
    },
)

# --- VISUALIZER THEME (Art / Diagrams) ---
VISUALIZER_THEME_DATA = ThemeRawData(
    name="visualizer",
    primary_color="purple",
    inquirer_style={
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
    },
)
