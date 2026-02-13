from dddguard.shared.domain import CodeNode, DirectionEnum, LayerEnum

from ...enums import ZoneKey


class PlacementLogic:
    """
    Stateless Logic: Determines where a node belongs in the Tower.
    Pure function wrapped in a namespace.
    """

    @staticmethod
    def resolve_zone(node: CodeNode) -> ZoneKey:
        if not node.passport:
            return ZoneKey.OTHER

        layer = node.passport.layer
        direction = node.passport.direction

        # 1. Split Layers
        if layer == LayerEnum.ADAPTERS:
            if direction == DirectionEnum.DRIVING:
                return ZoneKey.ADAPTERS_DRIVING
            if direction == DirectionEnum.DRIVEN:
                return ZoneKey.ADAPTERS_DRIVEN
            return ZoneKey.ADAPTERS_OTHER

        if layer == LayerEnum.PORTS:
            if direction == DirectionEnum.DRIVING:
                return ZoneKey.PORTS_DRIVING
            if direction == DirectionEnum.DRIVEN:
                return ZoneKey.PORTS_DRIVEN
            return ZoneKey.PORTS_OTHER

        # 2. Standard Layers
        if layer == LayerEnum.APP:
            return ZoneKey.APP

        if layer == LayerEnum.DOMAIN:
            return ZoneKey.DOMAIN

        if layer == LayerEnum.COMPOSITION:
            return ZoneKey.COMPOSITION

        return ZoneKey.OTHER
