from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True, kw_only=True, slots=True)
class RawLinkSchema:
    """
    Represents a physical import statement.
    """
    source: str
    target: str
    imported_symbols: List[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class RawNodeSchema:
    """
    Represents a detected module in the graph.
    """
    module_path: str
    is_visible: bool
    imports: List[RawLinkSchema]


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionStatsSchema:
    """
    Statistics regarding the physical scan.
    """
    total_files: int
    total_modules: int
    total_relations: int


@dataclass(frozen=True, kw_only=True, slots=True)
class DetectionResponseSchema:
    """
    The root DTO returned by the Detection Context.
    Contains the raw graph, the file tree structure, and stats.
    """
    graph_nodes: Dict[str, RawNodeSchema]
    source_tree: Dict[str, Any]
    stats: DetectionStatsSchema