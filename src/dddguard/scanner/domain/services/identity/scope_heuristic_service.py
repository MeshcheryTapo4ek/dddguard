from dataclasses import dataclass
from dddguard.shared import ProjectBoundedContextNames


@dataclass(frozen=True, kw_only=True, slots=True)
class ScopeHeuristicService:
    """
    Domain Service: Level 1 - Identifies the high-level scope (Context, Shared, Root).
    """

    def determine_scope(self, first_folder_name: str) -> ProjectBoundedContextNames:
        lower = first_folder_name.lower()

        if "root" in lower or "composition" in lower:
            return ProjectBoundedContextNames.COMPOSITION_ROOT

        if lower.startswith("shared"):
            return ProjectBoundedContextNames.SHARED

        return ProjectBoundedContextNames.CONTEXT