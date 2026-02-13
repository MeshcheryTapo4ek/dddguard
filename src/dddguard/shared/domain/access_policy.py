"""
Re-exports architectural access policy definitions.
This module serves as the canonical import point for policy rules.
"""

from ..assets.policy_data import (
    COMPOSITION_LAYERS,
    CROSS_CONTEXT_INBOUND_ALLOWED,
    CROSS_CONTEXT_OUTBOUND_ALLOWED,
    FRACTAL_DOWNSTREAM_ALLOWED,
    FRACTAL_DOWNSTREAM_FORBIDDEN,
    FRACTAL_UPSTREAM_ALLOWED,
    FRACTAL_UPSTREAM_FORBIDDEN,
    INTERNAL_ACCESS_MATRIX,
    AccessRule,
    InternalAccessMatrix,
    LayerDirectionKey,
    RuleName,
)

__all__ = [
    "COMPOSITION_LAYERS",
    "CROSS_CONTEXT_INBOUND_ALLOWED",
    "CROSS_CONTEXT_OUTBOUND_ALLOWED",
    "FRACTAL_DOWNSTREAM_ALLOWED",
    "FRACTAL_DOWNSTREAM_FORBIDDEN",
    "FRACTAL_UPSTREAM_ALLOWED",
    "FRACTAL_UPSTREAM_FORBIDDEN",
    "INTERNAL_ACCESS_MATRIX",
    "AccessRule",
    "InternalAccessMatrix",
    "LayerDirectionKey",
    "RuleName",
]
