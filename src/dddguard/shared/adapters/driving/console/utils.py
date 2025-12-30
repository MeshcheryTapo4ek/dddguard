from pathlib import Path
from typing import Optional


from .widgets import ask_path, DEFAULT_THEME


def ask_path_interactive(prompt_text: str = "Select path") -> Optional[Path]:
    """
    Legacy wrapper for the new powerful ask_path widget.
    """
    return ask_path(
        message=prompt_text,
        default=".",
        only_directories=True,
        must_exist=True,
        theme=DEFAULT_THEME,
    )
