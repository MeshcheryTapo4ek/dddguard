from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence
from dataclasses import dataclass, replace

from ...value_objects.options import OptimizationConfig, StyleConfig
from ...value_objects.visual_primitives import VisualContainer, VisualElement
from .dependency_weigher import DependencyWeigher, PairKey
from .flow_packer import FlowPacker, PackedResult


@dataclass(frozen=True, slots=True, kw_only=True)
class _GeomParams:
    pad_x: float
    pad_y: float
    header_h: float
    start_x: float
    start_y: float
    gap_x: float
    gap_y: float
    wrap_width_hint: float | None


class ContainerOptimizationService:
    """
    Domain Service: Optimizes ordering of sibling containers.
    PURE STATIC IMPLEMENTATION.
    Configuration is passed as arguments, making this service completely stateless.
    """

    @staticmethod
    def optimize_container_tree(
        container: VisualContainer,
        config: OptimizationConfig,
        style_config: StyleConfig,
    ) -> VisualContainer:
        """
        Coarse-to-fine optimization (Recursive).
        """
        # 1. Optimize current level
        optimized_self = ContainerOptimizationService._optimize_direct_children(
            container, config, style_config
        )

        # 2. Recurse down
        optimized_children: list[VisualElement] = []
        for ch in optimized_self.children:
            if isinstance(ch, VisualContainer):
                optimized_children.append(
                    ContainerOptimizationService.optimize_container_tree(ch, config, style_config)
                )
            else:
                optimized_children.append(ch)

        # 3. Recompute geometry based on new children
        return ContainerOptimizationService._recompute_container_geometry(
            replace(optimized_self, children=optimized_children), style_config
        )

    @staticmethod
    def optimize_sibling_list(
        siblings: Sequence[VisualContainer],
        config: OptimizationConfig,
        style_config: StyleConfig,
    ) -> list[VisualContainer]:
        """
        Optimize ordering of a flat list of sibling containers.
        """
        sibs = list(siblings)
        if len(sibs) < 2:
            return sibs

        if len(sibs) > config.max_children_guard:
            return sibs

        weights, adjacency = DependencyWeigher.calculate_weights(sibs)
        if not weights:
            return sibs

        rng = random.Random(ContainerOptimizationService._stable_seed_for_ids([c.id for c in sibs]))

        base_order = ContainerOptimizationService._create_smart_order(sibs, adjacency)

        best_order = base_order
        best_cost = ContainerOptimizationService._cost_for_sibling_order(
            sibs, best_order, weights, config, style_config
        )

        iterations = ContainerOptimizationService._scaled_iterations(len(sibs), config)
        restarts = max(0, int(config.restarts))

        for attempt in range(restarts + 1):
            if attempt == 0:
                current_order = base_order[:]
            else:
                current_order = base_order[:]
                rng.shuffle(current_order)

            current_cost = ContainerOptimizationService._cost_for_sibling_order(
                sibs, current_order, weights, config, style_config
            )
            local_best_order = current_order[:]
            local_best_cost = current_cost

            for _ in range(iterations):
                i, j = ContainerOptimizationService._pick_two_indices(rng, len(sibs))
                cand = local_best_order[:]
                cand[i], cand[j] = cand[j], cand[i]

                cand_cost = ContainerOptimizationService._cost_for_sibling_order(
                    sibs, cand, weights, config, style_config
                )
                if cand_cost < local_best_cost:
                    local_best_cost = cand_cost
                    local_best_order = cand

            if local_best_cost < best_cost:
                best_cost = local_best_cost
                best_order = local_best_order

        return [sibs[idx] for idx in best_order]

    @staticmethod
    def _optimize_direct_children(
        container: VisualContainer,
        config: OptimizationConfig,
        style_config: StyleConfig,
    ) -> VisualContainer:
        direct_children = [ch for ch in container.children if isinstance(ch, VisualContainer)]
        if len(direct_children) < 2:
            return container

        if len(direct_children) > config.max_children_guard:
            return container

        weights, adjacency = DependencyWeigher.calculate_weights(direct_children)
        external_anchors = ContainerOptimizationService._build_external_anchors(
            container, direct_children
        )

        if not weights and not external_anchors:
            return container

        params = ContainerOptimizationService._infer_geom_params(
            container, direct_children, style_config
        )
        rng = random.Random(
            ContainerOptimizationService._stable_seed_for_ids(
                [container.id] + [c.id for c in direct_children]
            )
        )

        base_order = ContainerOptimizationService._create_smart_order(direct_children, adjacency)

        best_order, best_packed, best_cost = ContainerOptimizationService._hill_climb_packed_order(
            rng=rng,
            children=direct_children,
            params=params,
            weights=weights,
            external_anchors=external_anchors,
            start_order=base_order,
            config=config,
        )

        restarts = max(0, int(config.restarts))
        for _ in range(restarts):
            start = base_order[:]
            rng.shuffle(start)
            cand_order, cand_packed, cand_cost = (
                ContainerOptimizationService._hill_climb_packed_order(
                    rng=rng,
                    children=direct_children,
                    params=params,
                    weights=weights,
                    external_anchors=external_anchors,
                    start_order=start,
                    config=config,
                )
            )
            if cand_cost < best_cost:
                best_cost = cand_cost
                best_order = cand_order
                best_packed = cand_packed

        ordered_refs = [direct_children[idx] for idx in best_order]
        remapped_children = ContainerOptimizationService._merge_positioned_children(
            original_parent=container,
            positioned_ordered_children=best_packed.positioned,
            ordered_child_refs=ordered_refs,
        )

        optimized = replace(container, children=remapped_children)
        return ContainerOptimizationService._recompute_container_geometry(optimized, style_config)

    @staticmethod
    def _create_smart_order(
        items: Sequence[VisualContainer], adjacency: dict[str, set[str]]
    ) -> list[int]:
        id_to_idx = {item.id: i for i, item in enumerate(items) if item.id}
        visited = set()
        order = []
        all_ids = sorted(list(id_to_idx.keys()))

        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            if node_id in id_to_idx:
                order.append(id_to_idx[node_id])
            children = sorted(list(adjacency.get(node_id, [])))
            for child_id in children:
                visit(child_id)

        for nid in all_ids:
            visit(nid)
        for i in range(len(items)):
            if i not in order:
                order.append(i)
        return order

    @staticmethod
    def _hill_climb_packed_order(
        *,
        rng: random.Random,
        children: Sequence[VisualContainer],
        params: _GeomParams,
        weights: dict[PairKey, float],
        external_anchors: dict[str, float],
        start_order: Sequence[int],
        config: OptimizationConfig,
    ) -> tuple[list[int], PackedResult, float]:
        best_order = list(start_order)
        best_packed = ContainerOptimizationService._pack_children_in_parent(
            children, best_order, params
        )
        best_cost = ContainerOptimizationService._cost_from_packed(
            best_packed, weights, external_anchors, params, config
        )
        iterations = ContainerOptimizationService._scaled_iterations(len(children), config)
        for _ in range(iterations):
            i, j = ContainerOptimizationService._pick_two_indices(rng, len(children))
            cand = best_order[:]
            cand[i], cand[j] = cand[j], cand[i]
            packed = ContainerOptimizationService._pack_children_in_parent(children, cand, params)
            cand_cost = ContainerOptimizationService._cost_from_packed(
                packed, weights, external_anchors, params, config
            )
            if cand_cost < best_cost:
                best_cost = cand_cost
                best_order = cand
                best_packed = packed
        return best_order, best_packed, best_cost

    @staticmethod
    def _build_external_anchors(
        parent: VisualContainer, children: Sequence[VisualContainer]
    ) -> dict[str, float]:
        anchors: dict[str, float] = {}
        leaf_to_child_id: dict[str, str] = {}
        for ch in children:
            if not ch.id:
                continue
            for leaf in ch.walk_leaves():
                if leaf.id:
                    leaf_to_child_id[leaf.id] = ch.id
        for leaf in parent.walk_leaves():
            if not leaf.id:
                continue
            src_child_id = leaf_to_child_id.get(leaf.id)
            if not src_child_id:
                continue
            for tgt_mod in leaf.outgoing_imports:
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

    @staticmethod
    def _infer_geom_params(
        parent: VisualContainer,
        children: Sequence[VisualContainer],
        style_config: StyleConfig,
    ) -> _GeomParams:
        is_leaf_wrapper = ContainerOptimizationService._is_probable_leaf_wrapper(parent)
        pad_x = style_config.CONTAINER_PAD_X if parent.is_visible else 0.0
        pad_y = style_config.CONTAINER_PAD_Y if parent.is_visible else 0.0

        header_h = 0.0

        if parent.is_visible and parent.label:
            header_h = 0.8 if not is_leaf_wrapper else 0.2

        start_x = pad_x
        start_y = header_h + pad_y
        has_only_containers = True
        for ch in parent.children:
            if not isinstance(ch, VisualContainer):
                has_only_containers = False
                break
        gap_x = style_config.CONTAINER_GAP_X if has_only_containers else style_config.LEAF_GAP_X
        gap_y = style_config.CONTAINER_GAP_Y if has_only_containers else style_config.LEAF_GAP_Y
        inner_width = parent.width
        if parent.is_visible:
            inner_width = max(0.0, parent.width - (pad_x * 2.0))
        max_child_w = 0.0
        for c in children:
            max_child_w = max(max_child_w, c.width)
        wrap_hint = max(inner_width, max_child_w) if inner_width > 0.0 else None
        return _GeomParams(
            pad_x=pad_x,
            pad_y=pad_y,
            header_h=header_h,
            start_x=start_x,
            start_y=start_y,
            gap_x=gap_x,
            gap_y=gap_y,
            wrap_width_hint=wrap_hint,
        )

    @staticmethod
    def _pack_children_in_parent(
        children: Sequence[VisualContainer], order: Sequence[int], params: _GeomParams
    ) -> PackedResult:
        ordered = [children[idx] for idx in order]
        return FlowPacker.pack(
            ordered,
            start_x=params.start_x,
            start_y=params.start_y,
            gap_x=params.gap_x,
            gap_y=params.gap_y,
            wrap_width_hint=params.wrap_width_hint,
        )

    @staticmethod
    def _recompute_container_geometry(
        container: VisualContainer, style_config: StyleConfig
    ) -> VisualContainer:
        if not container.children:
            return container
        if (not container.is_visible) and len(container.children) == 1:
            only = container.children[0]
            placed = replace(only, x=0.0, y=0.0)
            return replace(container, width=only.width, height=only.height, children=[placed])
        children = list(container.children)
        container_children = [c for c in children if isinstance(c, VisualContainer)]
        params = ContainerOptimizationService._infer_geom_params(
            container, container_children, style_config
        )
        packed = FlowPacker.pack(
            children,
            start_x=params.start_x,
            start_y=params.start_y,
            gap_x=params.gap_x,
            gap_y=params.gap_y,
            wrap_width_hint=params.wrap_width_hint,
        )
        total_w = packed.max_right + params.pad_x if container.is_visible else packed.max_right
        total_h = packed.max_bottom + params.pad_y if container.is_visible else packed.max_bottom
        return replace(container, width=total_w, height=total_h, children=packed.positioned)

    @staticmethod
    def _merge_positioned_children(
        *,
        original_parent: VisualContainer,
        positioned_ordered_children: Sequence[VisualElement],
        ordered_child_refs: Sequence[VisualContainer],
    ) -> list[VisualElement]:
        positioned_by_id = {}
        for el in positioned_ordered_children:
            if el.id:
                positioned_by_id[el.id] = el
        rebuilt = []
        for ch in ordered_child_refs:
            placed = positioned_by_id.get(ch.id)
            if placed:
                rebuilt.append(placed)
        for ch in original_parent.children:
            if isinstance(ch, VisualContainer):
                continue
            rebuilt.append(ch)
        return rebuilt

    @staticmethod
    def _cost_from_packed(
        packed: PackedResult,
        weights: dict[PairKey, float],
        external_anchors: dict[str, float],
        params: _GeomParams,
        config: OptimizationConfig,
    ) -> float:
        centers_by_id = {}
        for el in packed.positioned:
            if not el.id:
                continue
            cx = el.x + (el.width * 0.5)
            cy = el.y + (el.height * 0.5)
            centers_by_id[el.id] = (cx, cy)
        cost = 0.0
        for (id_a, id_b), w in weights.items():
            ca = centers_by_id.get(id_a)
            cb = centers_by_id.get(id_b)
            if ca is None or cb is None:
                continue
            dx = abs(ca[0] - cb[0])
            dy = abs(ca[1] - cb[1])
            cost += w * (dx + (config.lambda_y * dy))
        for child_id, target_y in external_anchors.items():
            center = centers_by_id.get(child_id)
            if center:
                cost += abs(center[1] - target_y) * config.external_attraction
        width = max(0.0, packed.max_right - params.start_x)
        height = max(0.0, packed.max_bottom - params.start_y)
        shape = config.shape_penalty * (width + height)
        return cost + shape

    @staticmethod
    def _cost_for_sibling_order(
        siblings: Sequence[VisualContainer],
        order: Sequence[int],
        weights: dict[PairKey, float],
        config: OptimizationConfig,
        style_config: StyleConfig,
    ) -> float:
        x_cursor = 0.0
        centers_by_id = {}
        for idx in order:
            s = siblings[idx]
            cx = x_cursor + (s.width * 0.5)
            cy = s.height * 0.5
            if s.id:
                centers_by_id[s.id] = (cx, cy)
            x_cursor = x_cursor + s.width + style_config.CONTAINER_GAP_X
        wire = 0.0
        for (id_a, id_b), w in weights.items():
            ca = centers_by_id.get(id_a)
            cb = centers_by_id.get(id_b)
            if ca and cb:
                wire += w * (abs(ca[0] - cb[0]) + (config.lambda_y * abs(ca[1] - cb[1])))
        return wire

    @staticmethod
    def _is_probable_leaf_wrapper(container: VisualContainer) -> bool:
        if len(container.children) != 1:
            return False
        only = container.children[0]
        return type(only).__name__ == "LeafNode" and container.label == only.label

    @staticmethod
    def _pick_two_indices(rng: random.Random, n: int) -> tuple[int, int]:
        i = rng.randrange(0, n)
        j = rng.randrange(0, n - 1)
        if j >= i:
            j = j + 1
        return i, j

    @staticmethod
    def _stable_seed_for_ids(ids: Sequence[str]) -> int:
        joined = "|".join([s for s in ids if s]).encode("utf-8")
        digest = hashlib.blake2b(joined, digest_size=8).digest()
        return int.from_bytes(digest, byteorder="big", signed=False)

    @staticmethod
    def _scaled_iterations(n_children: int, config: OptimizationConfig) -> int:
        base = int(config.iterations)
        if n_children <= 8:
            return base
        if n_children <= 14:
            return int(base * 0.7)
        return int(base * 0.45)
