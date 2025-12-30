from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True, kw_only=True, slots=True)
class InitProjectResponseSchema:
    """
    Driving Schema: Output data for the Project Initialization operation.
    Decouples the Adapter from internal Domain types.
    """

    success: bool
    config_path: Path
    message: str
    error_details: Optional[str] = None
