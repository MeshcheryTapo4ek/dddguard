import re
from dataclasses import dataclass

from dddguard.shared.domain import ArchetypeType, ComponentType, LayerEnum, MatchMethod

from .stage2_rule_prioritization import RuleCandidate


@dataclass(frozen=True, kw_only=True, slots=True)
class Stage3_4ComponentMatchingService:
    """
    Domain Service: Stages 3 & 4 - Component Matching.

    Executes the pattern matching logic using the prioritized rule pool.

    **Strategy: Fast-Fail Priority**
    1.  **Stage 3 (Structural):** Checks folders in the path. High confidence.
        (e.g., inside `/repositories/`).
    2.  **Stage 4 (Naming):** Checks the filename stem. Specific conventions.
        (e.g., `user_repository.py`).
    """

    @staticmethod
    def match_component(
        pool: tuple[RuleCandidate, ...],
        searchable_tokens: list[str],
        filename_stem: str,
    ) -> tuple[ComponentType, MatchMethod, LayerEnum]:
        """
        Executes the matching pipeline against the rule pool.

        :param pool: Prioritized rules from Stage 2.
        :param searchable_tokens: Cleaned path tokens from Stage 1.
        :param filename_stem: File name without extension.
        :return: Tuple(Type, Method, OriginLayer). Returns UNKNOWN if no match found.
        """

        # --- Stage 3: STRUCTURAL MATCH ---
        structural_type, origin_layer = Stage3_4ComponentMatchingService._run_match(
            pool, searchable_tokens
        )
        if structural_type != ArchetypeType.UNKNOWN:
            return structural_type, MatchMethod.STRUCTURAL, origin_layer

        # --- Stage 4: NAME MATCH ---
        name_type, origin_layer = Stage3_4ComponentMatchingService._run_match(pool, [filename_stem])
        if name_type != ArchetypeType.UNKNOWN:
            return name_type, MatchMethod.NAME, origin_layer

        return ArchetypeType.UNKNOWN, MatchMethod.UNKNOWN, LayerEnum.UNDEFINED

    @staticmethod
    def _run_match(
        pool: tuple[RuleCandidate, ...], tokens: list[str]
    ) -> tuple[ComponentType, LayerEnum]:
        """
        Iterates through the rule pool. First match wins.
        """
        for rule in pool:
            for token in tokens:
                if re.fullmatch(rule.regex, token, re.IGNORECASE):
                    return rule.comp_type, rule.origin_layer

        return ArchetypeType.UNKNOWN, LayerEnum.UNDEFINED
