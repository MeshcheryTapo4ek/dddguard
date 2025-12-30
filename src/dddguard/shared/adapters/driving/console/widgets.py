from pathlib import Path
from typing import Optional, List, Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import EmptyInputValidator

from .themes import GuardTheme, DEFAULT_THEME

# CLASSIFICATION:
# Scope: SHARED
# Layer: ADAPTERS (Tech dependent)
# Direction: ANY
# Type: HELPER (UI Widgets)


def ask_path(
    *,
    message: str = "Select directory",
    default: str = ".",
    only_directories: bool = True,
    must_exist: bool = True,
    root_path: str = ".",
    theme: GuardTheme = DEFAULT_THEME,
) -> Optional[Path]:
    """
    Interactive Fuzzy Directory Browser.
    """
    current_path = Path(default).resolve() if default else Path.cwd()
    if not current_path.exists():
        current_path = Path.cwd()

    while True:
        try:
            dirs = [
                d.name
                for d in current_path.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            dirs.sort()
        except PermissionError:
            current_path = current_path.parent
            continue

        choices = []
        choices.append(
            Choice(value=".", name=f"✅ SELECT CURRENT: {current_path.name}/")
        )

        if current_path.parent != current_path:
            choices.append(Choice(value="..", name="🔙 .. (Go Up)"))

        for d in dirs:
            choices.append(Choice(value=d, name=f"📂 {d}"))

        display_path = str(current_path)
        if len(display_path) > 50:
            display_path = "..." + display_path[-47:]

        msg_str = f"{message} (In: {display_path})"

        try:
            selection = inquirer.fuzzy(
                message=msg_str,
                choices=choices,
                default=None,
                style=theme.get_style(),
                qmark="🔍",
                pointer="❯",
                marker="",
                border=False,
                info=False,
                instruction="(Type to filter • Enter to navigate)",
                prompt="Filter: ",
            ).execute()
        except KeyboardInterrupt:
            return None

        if selection == ".":
            return current_path
        elif selection == "..":
            current_path = current_path.parent
        else:
            current_path = current_path / selection


def ask_text(
    *,
    message: str,
    default: str = "",
    allow_empty: bool = False,
    theme: GuardTheme = DEFAULT_THEME,
) -> Optional[str]:
    msg_str = f"{message}:" if message else ""
    try:
        return inquirer.text(
            message=msg_str,
            default=default,
            validate=EmptyInputValidator() if not allow_empty else None,
            style=theme.get_style(),
            qmark="📝",
            amark="✅",
            instruction="(Ctrl+C to cancel)",
        ).execute()
    except KeyboardInterrupt:
        return None


def ask_confirm(
    *, message: str, default: bool = True, theme: GuardTheme = DEFAULT_THEME
) -> bool:
    try:
        return inquirer.confirm(
            message=message,
            default=default,
            style=theme.get_style(),
            qmark="❓",
            amark="✅",
            instruction="(y/N)",
        ).execute()
    except KeyboardInterrupt:
        return False


def ask_select(
    *,
    message: str | None,
    choices: List[Any],
    default: Any = None,
    use_fuzzy: bool = False,
    multiselect: bool = False,
    theme: GuardTheme = DEFAULT_THEME,
    instruction: str = "",
) -> Any:
    msg_str = message if message is not None else ""
    if not instruction:
        instruction = "(Use arrow keys, Ctrl+C to cancel)"

    try:
        if use_fuzzy:
            return inquirer.fuzzy(
                message=msg_str,
                choices=choices,
                default=default,
                multiselect=multiselect,
                style=theme.get_style(),
                qmark="🔍",
                pointer="❯",
                marker="[x]",
                border=False,
                info=False,
                instruction=instruction,
                prompt="Filter: ",
            ).execute()
        else:
            return inquirer.select(
                message=msg_str,
                choices=choices,
                default=default,
                style=theme.get_style(),
                qmark="",
                amark="",
                pointer="❯",
                instruction=instruction,
            ).execute()
    except KeyboardInterrupt:
        return None


def ask_multiselect(
    *,
    message: str | None,
    choices: List[Any],
    theme: GuardTheme = DEFAULT_THEME,
    instruction: str = "(Space to select, Ctrl+C to cancel)",
) -> Optional[List[Any]]:
    msg_str = message if message is not None else ""
    try:
        return inquirer.checkbox(
            message=msg_str,
            choices=choices,
            style=theme.get_style(),
            qmark="",
            amark="",
            pointer="❯",
            enabled_symbol="[x]",
            disabled_symbol="[ ]",
            instruction=instruction,
            validate=lambda result: len(result) > 0 or "Select at least one option",
        ).execute()
    except KeyboardInterrupt:
        return None
