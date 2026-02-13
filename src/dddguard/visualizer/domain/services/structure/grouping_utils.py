import re
from re import Pattern

from dddguard.shared.domain import CodeNode

# Pre-compiled regex patterns for architectural noise
IGNORED_TOKENS: list[Pattern] = [
    # Layers
    re.compile(r"^domain$", re.IGNORECASE),
    re.compile(r"^app$", re.IGNORECASE),
    re.compile(r"^application$", re.IGNORECASE),
    re.compile(r"^ports?$", re.IGNORECASE),
    re.compile(r"^adapters?$", re.IGNORECASE),
    re.compile(r"^infrastructure$", re.IGNORECASE),
    re.compile(r"^composition$", re.IGNORECASE),
    re.compile(r"^wiring$", re.IGNORECASE),
    re.compile(r"^bootstrap$", re.IGNORECASE),
    # Directions
    re.compile(r"^driving$", re.IGNORECASE),
    re.compile(r"^inbound$", re.IGNORECASE),
    re.compile(r"^driven$", re.IGNORECASE),
    re.compile(r"^outbound$", re.IGNORECASE),
    # Common Technical Sub-folders
    re.compile(r"^src$", re.IGNORECASE),
]


class GroupingUtils:
    """
    Stateless Utility: Helper methods for analyzing file paths and structure.
    Used by StructureBuilderService to create the visual trie.
    """

    @staticmethod
    def get_semantic_path_parts(node: CodeNode) -> list[str]:
        """
        Returns the list of folder names representing the feature structure,
        stripping out architectural keywords (domain, app, ports, etc.).
        """
        # 1. Split path
        parts = node.path.split(".")

        # 2. Filter Logic
        semantic_parts = []

        # We iterate through parent folders (exclude filename at index -1)
        parent_folders = parts[:-1]

        context_name = (
            node.passport.context_name.lower()
            if node.passport and node.passport.context_name
            else ""
        )

        for token in parent_folders:
            # Skip context name (it's the Tower Root, not a folder inside)
            if token.lower() == context_name:
                continue

            # Skip ignored architectural tokens
            if GroupingUtils._is_ignored_token(token):
                continue

            semantic_parts.append(token)

        return semantic_parts

    @staticmethod
    def _is_ignored_token(token: str) -> bool:
        return any(pattern.match(token) for pattern in IGNORED_TOKENS)
