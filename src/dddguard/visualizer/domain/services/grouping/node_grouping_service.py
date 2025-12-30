import re
from dataclasses import dataclass
from typing import List, ClassVar, Pattern

from ....domain import DependencyNode


@dataclass(frozen=True, kw_only=True, slots=True)
class NodeGroupingService:
    """
    Domain Service: Logic for extracting the 'Semantic Path' of a node.
    It strips architectural tokens (layers, directions) to find the actual
    feature folder structure (e.g., 'orders/services' or 'billing/api').
    """

    # Regex patterns for tokens that should be ignored in the group path
    IGNORED_TOKENS: ClassVar[List[Pattern]] = [
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

    def get_semantic_path_parts(self, node: DependencyNode) -> List[str]:
        """
        Returns the list of folder names representing the feature structure.
        Example: 'src/ctx/domain/orders/models/order.py' -> ['orders', 'models']
        """
        # 1. Split path
        parts = node.module_path.split(".")
        
        # 2. Filter Logic
        semantic_parts = []
        
        # We iterate through parent folders (exclude filename at index -1)
        parent_folders = parts[:-1]

        for token in parent_folders:
            # Skip context name
            if token.lower() == node.context.lower():
                continue
            
            # Skip ignored architectural tokens
            if self._is_ignored_token(token):
                continue
            
            semantic_parts.append(token)

        return semantic_parts

    def extract_group_name(self, node: DependencyNode) -> str | None:
        """
        Legacy helper: returns joined path.
        """
        parts = self.get_semantic_path_parts(node)
        return "/".join(parts) if parts else None

    def _is_ignored_token(self, token: str) -> bool:
        for pattern in self.IGNORED_TOKENS:
            if pattern.match(token):
                return True
        return False