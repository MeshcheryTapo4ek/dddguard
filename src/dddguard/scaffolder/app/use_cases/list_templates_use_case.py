from dataclasses import dataclass
from typing import Dict, List, Tuple
from collections import defaultdict

from ..interfaces import ITemplateRepository
from ...domain import TemplateDefinition, CategoryDefinition


@dataclass(frozen=True, kw_only=True, slots=True)
class ListTemplatesUseCase:
    """
    App Service: Retrieves templates grouped by category, including category metadata.
    """
    template_repo: ITemplateRepository

    def execute(self) -> Tuple[Dict[str, CategoryDefinition], Dict[str, List[TemplateDefinition]]]:
        """
        Returns:
            Tuple containing:
            1. Dict of Category Definitions (ID -> Definition)
            2. Dict where Key is Category ID and Value is list of templates.
        """
        # 1. Load Metadata
        categories = self.template_repo.load_categories()
        all_templates = self.template_repo.load_all()
        
        # 2. Group Templates
        grouped = defaultdict(list)
        for tmpl in all_templates.values():
            grouped[tmpl.category].append(tmpl)
            
        return categories, dict(grouped)