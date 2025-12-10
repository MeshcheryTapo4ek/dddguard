import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from ...app import ITemplateRepository
from ...domain import TemplateDefinition, CategoryDefinition


@dataclass(frozen=True, kw_only=True, slots=True)
class DiskTemplateRepository(ITemplateRepository):
    """
    Reads templates from a local directory structure.
    """
    templates_dir: Path
    
    # Cache for paths
    _path_cache: Dict[str, Path] = None

    def get_template_source_path(self, template_id: str) -> Optional[Path]:
        if not self.templates_dir.exists():
            return None
            
        # Scan to find the path (simple scan)
        for category_path in self.templates_dir.iterdir():
            if not category_path.is_dir() or category_path.name.startswith("."):
                continue
            
            # Check direct match if folder name == ID
            candidate = category_path / template_id
            if candidate.exists():
                return candidate
            
            # Or inside check manifest (slower)
            for tmpl_path in category_path.iterdir():
                if not tmpl_path.is_dir(): continue
                
                manifest = self._find_manifest(tmpl_path, "manifest.json")
                if manifest:
                    try:
                        with open(manifest, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("id") == template_id:
                                return tmpl_path
                    except: pass
                elif tmpl_path.name == template_id:
                    return tmpl_path
                    
        return None

    def load_all(self) -> Dict[str, TemplateDefinition]:
        registry = {}
        if not self.templates_dir.exists():
            return registry

        for category_path in self.templates_dir.iterdir():
            if not category_path.is_dir() or category_path.name.startswith("."):
                continue

            category_name = category_path.name

            for template_path in category_path.iterdir():
                if not template_path.is_dir() or template_path.name.startswith("."):
                    continue
                
                # Check for manifest with .jinja preference
                manifest_file = self._find_manifest(template_path, "manifest.json")
                
                if manifest_file:
                    try:
                        definition = self._load_single_template(template_path, manifest_file, category_name)
                        registry[definition.id] = definition
                    except Exception as e:
                        print(f"Skipping invalid template at {template_path}: {e}")

        return registry

    def load_categories(self) -> Dict[str, CategoryDefinition]:
        categories = {}
        if not self.templates_dir.exists():
            return categories

        for category_path in self.templates_dir.iterdir():
            if not category_path.is_dir() or category_path.name.startswith("."):
                continue

            manifest_path = self._find_manifest(category_path, "template_category_manifest.json")
            
            if manifest_path:
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cat = CategoryDefinition(
                            id=category_path.name,
                            title=data.get("title", category_path.name),
                            description=data.get("description", "")
                        )
                        categories[cat.id] = cat
                except Exception:
                    categories[category_path.name] = self._create_fallback_category(category_path.name)
            else:
                categories[category_path.name] = self._create_fallback_category(category_path.name)
                
        return categories

    def _load_single_template(self, root_path: Path, manifest_file: Path, category: str) -> TemplateDefinition:
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        # ID defaults to folder name if missing
        tmpl_id = manifest.get("id", root_path.name)
        description = manifest.get("description", "")
        deps = manifest.get("dependencies", [])

        # Extract extra metadata (everything excluding known keys)
        reserved_keys = {"id", "description", "dependencies", "category"}
        metadata = {k: v for k, v in manifest.items() if k not in reserved_keys}

        files_map = {}
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            
            for filename in files:
                # Ignore manifests and pyc files in the file map
                if "manifest.json" in filename or filename.endswith(".pyc"):
                    continue
                
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(root_path).as_posix()
                
                with open(full_path, "r", encoding="utf-8") as f:
                    files_map[rel_path] = f.read()

        return TemplateDefinition(
            id=tmpl_id,
            category=category,
            description=description,
            dependencies=deps,
            files=files_map,
            metadata=metadata
        )

    def _find_manifest(self, folder: Path, base_name: str) -> Optional[Path]:
        """
        Looks for 'base_name.jinja' first, then 'base_name'.
        Returns the path to the file if found, else None.
        """
        # Priority 1: .jinja suffix
        jinja_path = folder / f"{base_name}.jinja"
        if jinja_path.exists():
            return jinja_path
        
        # Priority 2: Exact match
        exact_path = folder / base_name
        if exact_path.exists():
            return exact_path
            
        return None

    def _create_fallback_category(self, name: str) -> CategoryDefinition:
        return CategoryDefinition(
            id=name,
            title=name.replace("_", " ").title(),
            description=""
        )