from dataclasses import dataclass
from typing import Dict, Set, Tuple, Deque
from collections import deque

from .entities import DependencyGraph
from .value_objects import ScannedModuleVo, PathFilter


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyExpansionService:
    """
    Domain Service: Raw graph traversal and filtering.
    """

    def apply_path_filters(
        self,
        graph: DependencyGraph,
        registry: Dict[str, ScannedModuleVo],
        path_filter: PathFilter,
    ) -> None:
        """
        Mark nodes as visible if they satisfy the PathFilter criteria.
        """
        for node in graph.all_nodes:
            module_vo = registry.get(node.module_path)
            if not module_vo:
                continue

            # Delegated logic: simple and cleaner
            if path_filter.is_relevant(module_vo.file_path):
                node.is_visible = True

    def expand_by_imports(
        self,
        graph: DependencyGraph,
        registry: Dict[str, ScannedModuleVo],
        initial_budget: int,
    ) -> None:
        """
        BFS Traversal to include imported modules up to a certain depth.
        """
        queue: Deque[Tuple[str, int, Set[str]]] = deque()
        
        # Init queue
        for node in graph.visible_nodes:
            node.remaining_depth = initial_budget
            queue.append((node.module_path, initial_budget, set()))

        visited_states: Dict[Tuple[str, frozenset], int] = {}

        while queue:
            current_path, budget, required_symbols = queue.popleft()

            state_key = (current_path, frozenset(required_symbols))
            if state_key in visited_states and visited_states[state_key] >= budget:
                continue
            visited_states[state_key] = budget

            if budget < 0:
                continue

            current_node = graph.get_node(current_path)
            if not current_node:
                continue

            for link in current_node.imports:
                target_path = link.target_module
                target_node = graph.get_node(target_path)
                target_vo = registry.get(target_path)
                
                if not target_node or not target_vo:
                    continue

                symbols_to_pass_down = set()
                should_follow = True
                
                if required_symbols and target_vo.is_package:
                     provided = set(link.imported_symbols).intersection(required_symbols)
                     if provided:
                         symbols_to_pass_down = provided
                     else:
                         should_follow = False

                if not should_follow:
                    continue

                cost = 0 if target_vo.is_package else 1
                new_budget = budget - cost

                if new_budget >= 0:
                    if not target_node.is_visible:
                        target_node.is_visible = True
                        target_node.remaining_depth = new_budget
                    
                    if new_budget > target_node.remaining_depth:
                        target_node.remaining_depth = new_budget

                    queue.append((target_path, new_budget, symbols_to_pass_down))