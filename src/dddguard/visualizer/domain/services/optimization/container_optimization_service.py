from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, replace
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Set

from dddguard.shared import LayerEnum

from ...value_objects.visual_primitives import LeafNode, VisualContainer, VisualElement
from ..styling.style_service import StyleService
from .flow_packing_service import FlowPackingService, PackedResult
from .optimization_config import OptimizationConfig

PairKey = Tuple[str, str]

@dataclass(frozen=True, slots=True, kw_only=True)
class _GeomParams:
    pad_x: float
    pad_y: float
    header_h: float
    start_x: float
    start_y: float
    gap_x: float
    gap_y: float
    wrap_width_hint: Optional[float]


@dataclass(frozen=True, slots=True, kw_only=True)
class ContainerOptimizationService:
    """
    Domain Service: optimizes ordering of sibling containers.
    Includes smart topological initialization to cluster connected items.
    """

    style: StyleService
    config: OptimizationConfig
    packer: FlowPackingService = FlowPackingService()

    def optimize_container_tree(self, container: VisualContainer) -> VisualContainer:
        """
        Coarse-to-fine optimization.
        """
        optimized_self = self._optimize_direct_children(container)

        optimized_children: List[VisualElement] = []
        for ch in optimized_self.children:
            if isinstance(ch, VisualContainer):
                optimized_children.append(self.optimize_container_tree(ch))
            else:
                optimized_children.append(ch)

        return self._recompute_container_geometry(replace(optimized_self, children=optimized_children))

    def optimize_sibling_list(self, siblings: Sequence[VisualContainer]) -> List[VisualContainer]:
        """
        Optimize ordering of a flat list of sibling containers.
        """
        sibs = list(siblings)
        if len(sibs) < 2:
            return sibs

        if len(sibs) > self.config.max_children_guard:
            return sibs

        # 1. Build weights and directional graph for sorting
        weights, adjacency = self._build_graph_for_siblings(sibs)
        
        if not weights:
            return sibs

        rng = random.Random(self._stable_seed_for_ids([c.id for c in sibs]))

        # 2. Smart Initialization (Topological Cluster Sort)
        # Instead of 0..N, we generate an order that respects dependencies
        base_order = self._create_smart_order(sibs, adjacency)
        
        best_order = base_order
        best_cost = self._cost_for_sibling_order(sibs, best_order, weights)

        iterations = self._scaled_iterations(len(sibs))
        restarts = max(0, int(self.config.restarts))

        for attempt in range(restarts + 1):
            if attempt == 0:
                current_order = base_order[:]
            else:
                current_order = base_order[:]
                rng.shuffle(current_order)

            current_cost = self._cost_for_sibling_order(sibs, current_order, weights)
            local_best_order = current_order[:]
            local_best_cost = current_cost

            for _ in range(iterations):
                i, j = self._pick_two_indices(rng, len(sibs))
                cand = local_best_order[:]
                cand[i], cand[j] = cand[j], cand[i]

                cand_cost = self._cost_for_sibling_order(sibs, cand, weights)
                if cand_cost < local_best_cost:
                    local_best_cost = cand_cost
                    local_best_order = cand

            if local_best_cost < best_cost:
                best_cost = local_best_cost
                best_order = local_best_order

        return [sibs[idx] for idx in best_order]

    def _optimize_direct_children(self, container: VisualContainer) -> VisualContainer:
        direct_children = [ch for ch in container.children if isinstance(ch, VisualContainer)]
        if len(direct_children) < 2:
            return container

        if len(direct_children) > self.config.max_children_guard:
            return container

        # 1. Internal Weights & Graph
        weights, adjacency = self._build_graph_for_parent(container, direct_children)
        
        # 2. External Anchors
        external_anchors = self._build_external_anchors(container, direct_children)

        if not weights and not external_anchors:
            return container

        params = self._infer_geom_params(container, direct_children)
        rng = random.Random(self._stable_seed_for_ids([container.id] + [c.id for c in direct_children]))

        # SMART INIT: Use topological sort as the base "DNA"
        base_order = self._create_smart_order(direct_children, adjacency)

        best_order, best_packed, best_cost = self._hill_climb_packed_order(
            rng=rng,
            children=direct_children,
            params=params,
            weights=weights,
            external_anchors=external_anchors,
            start_order=base_order,
        )

        restarts = max(0, int(self.config.restarts))
        for _ in range(restarts):
            start = base_order[:]
            rng.shuffle(start)
            cand_order, cand_packed, cand_cost = self._hill_climb_packed_order(
                rng=rng,
                children=direct_children,
                params=params,
                weights=weights,
                external_anchors=external_anchors,
                start_order=start,
            )
            if cand_cost < best_cost:
                best_cost = cand_cost
                best_order = cand_order
                best_packed = cand_packed

        ordered_refs = [direct_children[idx] for idx in best_order]
        remapped_children = self._merge_positioned_children(
            original_parent=container,
            positioned_ordered_children=best_packed.positioned,
            ordered_child_refs=ordered_refs,
        )

        optimized = replace(container, children=remapped_children)
        return self._recompute_container_geometry(optimized)

    # --- SMART INITIALIZATION LOGIC ---

    def _create_smart_order(
        self, 
        items: Sequence[VisualContainer], 
        adjacency: Dict[str, Set[str]]
    ) -> List[int]:
        """
        Creates a topological-ish ordering where dependencies are placed 
        immediately after their dependents.
        This clusters connected items (Workflow -> UseCase -> Interface).
        """
        # Map IDs to current indices
        id_to_idx = {item.id: i for i, item in enumerate(items) if item.id}
        visited = set()
        order = []

        # Find items that have NO incoming edges (Roots) to start the traversal.
        # But here we only have adjacency (outgoing).
        # We just iterate all.
        
        # Sort keys to be deterministic
        all_ids = sorted(list(id_to_idx.keys()))

        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            
            # Place the node
            if node_id in id_to_idx:
                order.append(id_to_idx[node_id])
            
            # Immediately visit children (Depth-First) to keep them close
            children = sorted(list(adjacency.get(node_id, [])))
            for child_id in children:
                visit(child_id)

        for nid in all_ids:
            visit(nid)

        # Append any items without IDs or missed
        for i in range(len(items)):
            if i not in order:
                order.append(i)
                
        return order

    # --- GRAPH BUILDERS (Returns Weights + Adjacency) ---

    def _build_graph_for_siblings(self, siblings: Sequence[VisualContainer]) -> Tuple[Dict[PairKey, float], Dict[str, Set[str]]]:
        leaf_to_sib_id: Dict[str, str] = {}
        for sib in siblings:
            for leaf in self._iter_leaves(sib):
                if leaf.id: leaf_to_sib_id[leaf.id] = sib.id
        
        if not leaf_to_sib_id: return {}, {}

        weights: Dict[PairKey, float] = {}
        adjacency: Dict[str, Set[str]] = {}

        for sib in siblings:
            if not sib.id: continue
            if sib.id not in adjacency: adjacency[sib.id] = set()

            for leaf in self._iter_leaves(sib):
                if not leaf.id: continue
                src_sib_id = leaf_to_sib_id.get(leaf.id)
                if not src_sib_id: continue

                for imp in leaf.outgoing_imports:
                    tgt_leaf_id = imp.get("module")
                    if not tgt_leaf_id: continue
                    tgt_sib_id = leaf_to_sib_id.get(tgt_leaf_id)
                    
                    if tgt_sib_id is None or tgt_sib_id == src_sib_id: continue

                    # Adjacency (Directed)
                    adjacency[src_sib_id].add(tgt_sib_id)

                    # Weights (Symmetric)
                    a, b = (src_sib_id, tgt_sib_id) if src_sib_id < tgt_sib_id else (tgt_sib_id, src_sib_id)
                    key: PairKey = (a, b)
                    weights[key] = weights.get(key, 0.0) + 1.0
        
        return weights, adjacency

    def _build_graph_for_parent(
        self,
        parent: VisualContainer,
        direct_children: Sequence[VisualContainer],
    ) -> Tuple[Dict[PairKey, float], Dict[str, Set[str]]]:
        leaf_to_child_id: Dict[str, str] = {}
        for ch in direct_children:
            for leaf in self._iter_leaves(ch):
                if leaf.id: leaf_to_child_id[leaf.id] = ch.id

        if not leaf_to_child_id: return {}, {}

        weights: Dict[PairKey, float] = {}
        adjacency: Dict[str, Set[str]] = {}

        for leaf in self._iter_leaves(parent):
            if not leaf.id: continue
            src_child_id = leaf_to_child_id.get(leaf.id)
            if src_child_id is None: continue
            
            if src_child_id not in adjacency: adjacency[src_child_id] = set()

            for imp in leaf.outgoing_imports:
                tgt_leaf_id = imp.get("module")
                if not tgt_leaf_id: continue
                tgt_child_id = leaf_to_child_id.get(tgt_leaf_id)
                
                if tgt_child_id is None or tgt_child_id == src_child_id: continue

                # Adjacency (Directed)
                adjacency[src_child_id].add(tgt_child_id)

                # Weights (Symmetric)
                a, b = (src_child_id, tgt_child_id) if src_child_id < tgt_child_id else (tgt_child_id, src_child_id)
                key: PairKey = (a, b)
                weights[key] = weights.get(key, 0.0) + 1.0

        return weights, adjacency

    # --- EXISTING HELPERS (Unchanged) ---

    def _hill_climb_packed_order(
        self,
        *,
        rng: random.Random,
        children: Sequence[VisualContainer],
        params: _GeomParams,
        weights: Dict[PairKey, float],
        external_anchors: Dict[str, float], 
        start_order: Sequence[int],
    ) -> Tuple[List[int], PackedResult, float]:
        best_order = list(start_order)
        best_packed = self._pack_children_in_parent(children, best_order, params)
        best_cost = self._cost_from_packed(best_packed, weights, external_anchors, params)

        iterations = self._scaled_iterations(len(children))

        for _ in range(iterations):
            i, j = self._pick_two_indices(rng, len(children))
            cand = best_order[:]
            cand[i], cand[j] = cand[j], cand[i]

            packed = self._pack_children_in_parent(children, cand, params)
            cand_cost = self._cost_from_packed(packed, weights, external_anchors, params)

            if cand_cost < best_cost:
                best_cost = cand_cost
                best_order = cand
                best_packed = packed

        return best_order, best_packed, best_cost

    def _build_external_anchors(
        self, 
        parent: VisualContainer, 
        children: Sequence[VisualContainer]
    ) -> Dict[str, float]:
        anchors: Dict[str, float] = {}
        leaf_to_child_id: Dict[str, str] = {}
        child_ids = set(c.id for c in children)

        for ch in children:
            for leaf in self._iter_leaves(ch):
                if leaf.id:
                    leaf_to_child_id[leaf.id] = ch.id
        
        for leaf in self._iter_leaves(parent):
            if not leaf.id: continue
            src_child_id = leaf_to_child_id.get(leaf.id)
            if not src_child_id: continue

            for imp in leaf.outgoing_imports:
                tgt_mod = imp.get("module", "")
                target_y = None
                if ".driving" in tgt_mod or ".api" in tgt_mod or ".entrypoints" in tgt_mod:
                     target_y = 0.0 
                elif ".driven" in tgt_mod or ".db" in tgt_mod or ".adapters" in tgt_mod:
                     target_y = 10000.0 
                
                if target_y is not None:
                    if src_child_id in anchors:
                         anchors[src_child_id] = (anchors[src_child_id] + target_y) / 2.0
                    else:
                         anchors[src_child_id] = target_y
        return anchors

    def _infer_geom_params(self, parent: VisualContainer, children: Sequence[VisualContainer]) -> _GeomParams:
        is_leaf_wrapper = self._is_probable_leaf_wrapper(parent)
        pad_x = self.style.CONTAINER_PAD_X if parent.is_visible else 0.0
        pad_y = self.style.CONTAINER_PAD_Y if parent.is_visible else 0.0
        header_h = 0.0
        if parent.is_visible and not is_leaf_wrapper:
            header_h = 0.8
        if parent.is_visible and is_leaf_wrapper:
            header_h = 0.2
        start_x = pad_x
        start_y = header_h + pad_y
        has_only_containers = True
        for ch in parent.children:
            if not isinstance(ch, VisualContainer):
                has_only_containers = False
                break
        gap_x = self.style.CONTAINER_GAP_X if has_only_containers else self.style.LEAF_GAP_X
        gap_y = self.style.CONTAINER_GAP_Y if has_only_containers else self.style.LEAF_GAP_Y
        inner_width = parent.width
        if parent.is_visible:
            inner_width = max(0.0, parent.width - (pad_x * 2.0))
        max_child_w = 0.0
        for c in children:
            max_child_w = max(max_child_w, c.width)
        wrap_hint = max(inner_width, max_child_w) if inner_width > 0.0 else None
        return _GeomParams(
            pad_x=pad_x, pad_y=pad_y, header_h=header_h,
            start_x=start_x, start_y=start_y,
            gap_x=gap_x, gap_y=gap_y, wrap_width_hint=wrap_hint,
        )

    def _pack_children_in_parent(self, children: Sequence[VisualContainer], order: Sequence[int], params: _GeomParams) -> PackedResult:
        ordered = [children[idx] for idx in order]
        return self.packer.pack(
            ordered,
            start_x=params.start_x,
            start_y=params.start_y,
            gap_x=params.gap_x,
            gap_y=params.gap_y,
            wrap_width=params.wrap_width_hint,
        )

    def _recompute_container_geometry(self, container: VisualContainer) -> VisualContainer:
        if not container.children:
            return container
        if (not container.is_visible) and len(container.children) == 1:
            only = container.children[0]
            placed = replace(only, x=0.0, y=0.0)
            return replace(container, width=only.width, height=only.height, children=[placed])
        children = list(container.children)
        container_children = [c for c in children if isinstance(c, VisualContainer)]
        params = self._infer_geom_params(container, container_children)
        packed = self.packer.pack(
            children,
            start_x=params.start_x,
            start_y=params.start_y,
            gap_x=params.gap_x,
            gap_y=params.gap_y,
            wrap_width=params.wrap_width_hint,
        )
        total_w = packed.max_right + params.pad_x if container.is_visible else packed.max_right
        total_h = packed.max_bottom + params.pad_y if container.is_visible else packed.max_bottom
        return replace(container, width=total_w, height=total_h, children=packed.positioned)

    def _merge_positioned_children(self, *, original_parent: VisualContainer, positioned_ordered_children: Sequence[VisualElement], ordered_child_refs: Sequence[VisualContainer]) -> List[VisualElement]:
        positioned_by_id = {}
        for el in positioned_ordered_children:
            if el.id: positioned_by_id[el.id] = el
        rebuilt = []
        for ch in ordered_child_refs:
            placed = positioned_by_id.get(ch.id)
            if placed: rebuilt.append(placed)
        for ch in original_parent.children:
            if isinstance(ch, VisualContainer): continue
            rebuilt.append(ch)
        return rebuilt

    def _cost_from_packed(
        self, 
        packed: PackedResult, 
        weights: Dict[PairKey, float], 
        external_anchors: Dict[str, float],
        params: _GeomParams
    ) -> float:
        centers_by_id: Dict[str, Tuple[float, float]] = {}
        for el in packed.positioned:
            if not el.id: continue
            cx = el.x + (el.width * 0.5)
            cy = el.y + (el.height * 0.5)
            centers_by_id[el.id] = (cx, cy)

        cost = 0.0
        for (id_a, id_b), w in weights.items():
            ca = centers_by_id.get(id_a)
            cb = centers_by_id.get(id_b)
            if ca is None or cb is None: continue
            dx = abs(ca[0] - cb[0])
            dy = abs(ca[1] - cb[1])
            cost += (w * (dx + (self.config.lambda_y * dy)))

        for child_id, target_y in external_anchors.items():
            center = centers_by_id.get(child_id)
            if center:
                cy = center[1]
                dist_y = abs(cy - target_y)
                cost += (dist_y * self.config.external_attraction)

        width = max(0.0, packed.max_right - params.start_x)
        height = max(0.0, packed.max_bottom - params.start_y)
        shape = self.config.shape_penalty * (width + height)

        return cost + shape

    def _cost_for_sibling_order(self, siblings: Sequence[VisualContainer], order: Sequence[int], weights: Dict[PairKey, float]) -> float:
        x_cursor = 0.0
        centers_by_id = {}
        for idx in order:
            s = siblings[idx]
            cx = x_cursor + (s.width * 0.5)
            cy = s.height * 0.5
            if s.id: centers_by_id[s.id] = (cx, cy)
            x_cursor = x_cursor + s.width + self.style.CONTAINER_GAP_X
        wire = 0.0
        for (id_a, id_b), w in weights.items():
            ca = centers_by_id.get(id_a)
            cb = centers_by_id.get(id_b)
            if ca and cb:
                wire += (w * (abs(ca[0] - cb[0]) + (self.config.lambda_y * abs(ca[1] - cb[1]))))
        return wire

    def _iter_leaves(self, element: VisualElement) -> Iterable[LeafNode]:
        if isinstance(element, LeafNode):
            yield element
            return
        if isinstance(element, VisualContainer):
            for ch in element.children:
                yield from self._iter_leaves(ch)

    def _is_probable_leaf_wrapper(self, container: VisualContainer) -> bool:
        if len(container.children) != 1: return False
        only = container.children[0]
        if not isinstance(only, LeafNode): return False
        return container.label == only.label

    def _pick_two_indices(self, rng: random.Random, n: int) -> Tuple[int, int]:
        i = rng.randrange(0, n)
        j = rng.randrange(0, n - 1)
        if j >= i: j = j + 1
        return i, j

    def _stable_seed_for_ids(self, ids: Sequence[str]) -> int:
        joined = "|".join([s for s in ids if s]).encode("utf-8")
        digest = hashlib.blake2b(joined, digest_size=8).digest()
        return int.from_bytes(digest, byteorder="big", signed=False)

    def _scaled_iterations(self, n_children: int) -> int:
        base = int(self.config.iterations)
        if n_children <= 8: return base
        if n_children <= 14: return int(base * 0.7)
        return int(base * 0.45)