from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..helpers.generics.errors import GenericDomainError
from .architecture_enums import (
    ComponentType,
    DirectionEnum,
    LayerEnum,
    MatchMethod,
    ScopeEnum,
)

# Constant for "unlimited" visibility radius (no filtering applied)
UNLIMITED_RADIUS: int = 999


# --- 1. Value Object / Enum (Local Cohesion) ---
class NodeStatus(str, Enum):
    """
    Lifecycle states of a CodeNode.

    DETECTED - Raw file found, no connections yet
    LINKED - Imports parsed, neighbors established
    CLASSIFIED - Architectural Passport assigned
    FINALIZED - Ready for reporting (visibility calculated)
    """

    DETECTED = "DETECTED"
    LINKED = "LINKED"
    CLASSIFIED = "CLASSIFIED"
    FINALIZED = "FINALIZED"


@dataclass(frozen=True, slots=True, kw_only=True)
class ComponentPassport:
    """
    Architectural ID Card of a component.
    """

    scope: ScopeEnum
    context_name: str | None
    macro_zone: str | None
    layer: LayerEnum
    direction: DirectionEnum
    component_type: ComponentType
    match_method: MatchMethod


# --- 2. Entity (The Atom) ---
@dataclass(slots=True)
class CodeNode:
    """
    Domain Entity: Represents a single Python module (file) in the system.
    It is a mutable State Machine that evolves during the analysis phases.
    """

    # Identity
    path: str

    # Physical Location (for filtering and classification context)
    file_path: Path | None = None

    # Content (for deep analysis and reporting)
    content: str | None = None

    # State
    _status: NodeStatus = field(default=NodeStatus.DETECTED)

    # Relations & Metadata
    imports: set[str] = field(default_factory=set)
    passport: ComponentPassport | None = None
    visible_radius: int = UNLIMITED_RADIUS

    @property
    def status(self) -> NodeStatus:
        return self._status

    def link_imports(self, imports: list[str]) -> None:
        """
        Transition: DETECTED -> LINKED.
        """
        self.imports = set(imports)
        self._status = NodeStatus.LINKED

    def classify(self, passport: ComponentPassport) -> None:
        """
        Transition: LINKED -> CLASSIFIED.
        """
        self.passport = passport
        self._status = NodeStatus.CLASSIFIED

    def finalize(self) -> None:
        """
        Transition: CLASSIFIED -> FINALIZED.
        """
        if not self.passport:
            raise GenericDomainError(
                f"Cannot finalize node {self.path}: missing passport.",
                context_name="Shared",
            )

        self._status = NodeStatus.FINALIZED


# --- 3. Aggregate Root (The Universe) ---


@dataclass(slots=True)
class CodeGraph:
    """
    Aggregate Root: Encapsulates the entire graph of code nodes.
    Maintains consistency and provides aggregate-level statistics.
    """

    nodes: dict[str, CodeNode] = field(default_factory=dict)

    def add_node(
        self,
        path: str,
        file_path: Path | None = None,
        content: str | None = None,
    ) -> CodeNode:
        """Creates and registers a new node if it doesn't exist."""
        if path not in self.nodes:
            self.nodes[path] = CodeNode(path=path, file_path=file_path, content=content)
        return self.nodes[path]

    def get_node(self, path: str) -> CodeNode | None:
        return self.nodes.get(path)

    @property
    def total_files(self) -> int:
        return len(self.nodes)

    @property
    def classified_count(self) -> int:
        return sum(
            1
            for n in self.nodes.values()
            if n.status in (NodeStatus.CLASSIFIED, NodeStatus.FINALIZED)
        )

    @property
    def coverage_percent(self) -> float:
        """Returns the % of files that were successfully classified."""
        if self.total_files == 0:
            return 0.0
        return round((self.classified_count / self.total_files) * 100, 2)
