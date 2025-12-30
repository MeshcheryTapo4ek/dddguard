from dataclasses import dataclass
from typing import Dict, Set, Tuple, Deque
from collections import deque

from dddguard.shared.domain import ScopeEnum

from ..entities import DependencyGraph
from ..value_objects import ScannedModuleVo


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyExpansionService:
    """
    Domain Service: Encapsulates the graph traversal algorithms.
    Responsible for:
    1. Visibility Filtering (hiding irrelevant nodes).
    2. Smart Expansion (BFS with Cost 0/1 logic for re-exports).
    """

    def apply_visibility_filters(
        self,
        graph: DependencyGraph,
        registry: Dict[str, ScannedModuleVo],
        focus_path: str,
        whitelist_contexts: Set[str] | None,
        whitelist_layers: Set[str] | None,
    ) -> None:
        """
        Mark nodes as is_visible=True based on strict architectural filters.
        """
        # --- Normalization Phase ---
        # Convert whitelist to Upper Case Strings to handle Enum vs String mismatches
        # and Case Sensitivity issues (e.g. "Adapters" vs "ADAPTERS")
        allowed_layers_norm: Set[str] | None = None
        if whitelist_layers:
            allowed_layers_norm = {str(l).upper() for l in whitelist_layers}

        for node in graph.all_nodes:
            module_vo = registry.get(node.module_path)
            if not module_vo:
                continue

            # Check if file is physically within the focused directory
            if not str(module_vo.file_path).startswith(str(focus_path)):
                continue

            # Context Filter (Exact Match usually required as these are folder names)
            if whitelist_contexts and node.context not in whitelist_contexts:
                continue
            
            # Layer Filter (Case-Insensitive Robust Match)
            if allowed_layers_norm:
                node_layer_str = str(node.layer).upper()
                if node_layer_str not in allowed_layers_norm:
                    continue
            
            node.is_visible = True

    def expand_visibility_by_imports(
        self,
        graph: DependencyGraph,
        registry: Dict[str, ScannedModuleVo],
        initial_budget: int,
    ) -> None:
        """
        Symbol-Aware Propagation Algorithm.
        """
        # Queue: (path, budget, symbols_we_are_looking_for)
        queue: Deque[Tuple[str, int, Set[str]]] = deque()
        
        # Initialize from currently visible nodes
        for node in graph.visible_nodes:
            node.remaining_depth = initial_budget
            # Root nodes initiate a wildcard search (empty set)
            queue.append((node.module_path, initial_budget, set()))

        # To prevent infinite loops: (module_path, frozenset(symbols)) -> max_budget_seen
        visited_states: Dict[Tuple[str, frozenset], int] = {}

        while queue:
            current_path, budget, required_symbols = queue.popleft()

            # State Check & Memoization
            state_key = (current_path, frozenset(required_symbols))
            if state_key in visited_states and visited_states[state_key] >= budget:
                continue
            visited_states[state_key] = budget

            if budget < 0:
                continue

            current_node = graph.get_node(current_path)
            current_vo = registry.get(current_path)
            
            if not current_node or not current_vo:
                continue

            # Iterate over outgoing links
            for link in current_node.imports:
                target_path = link.target_module
                target_node = graph.get_node(target_path)
                target_vo = registry.get(target_path)
                
                if not target_node or not target_vo:
                    continue

                # --- SYMBOL FILTERING LOGIC ---
                symbols_to_pass_down = set()
                should_follow = False

                # Case 1: Re-export traversal (looking for specific symbol in a package)
                if required_symbols and current_vo.is_package:
                    provided = set(link.imported_symbols).intersection(required_symbols)
                    if provided:
                        should_follow = True
                        symbols_to_pass_down = provided
                
                # Case 2: Wildcard traversal (Root node or wildcard import)
                elif not required_symbols:
                    should_follow = True
                    symbols_to_pass_down = set(link.imported_symbols)
                
                # Case 3: Dead end for these symbols
                else:
                    should_follow = False

                if not should_follow:
                    continue

                # --- COST CALCULATION ---
                # Smart Depth: Traversing packages is free (Cost 0)
                cost = 0 if target_vo.is_package else 1
                new_budget = budget - cost

                if new_budget >= 0:
                    # Activate Target
                    if not target_node.is_visible:
                        target_node.is_visible = True
                        target_node.remaining_depth = new_budget
                    
                    if new_budget > target_node.remaining_depth:
                        target_node.remaining_depth = new_budget

                    # Continue traversal
                    if target_vo.is_package:
                        # Keep looking for specific symbols
                        queue.append((target_path, new_budget, symbols_to_pass_down))
                    else:
                        # Reached implementation. Should we go deeper?
                        if new_budget > 0:
                             queue.append((target_path, new_budget, set()))