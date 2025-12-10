import yaml
import re
from typing import Dict, List, Set, Any, Tuple, Optional
from jinja2 import Environment, BaseLoader, TemplateError

from .value_objects import TemplateDefinition, RenderedFileVo
from .errors import TemplateRenderingError

def to_pascal_case(snake_str: str) -> str:
    if not snake_str:
        return ""
    return "".join(word.title() for word in snake_str.split("_"))

class TemplateCompositor:
    def __init__(self):
        # Reverted StrictUndefined to allow {% if var %} checks to fail gracefully
        self._jinja_env = Environment(
            loader=BaseLoader(), 
            keep_trailing_newline=True
        )
        self._jinja_env.filters["pascal"] = to_pascal_case

    def compose(
        self,
        root_template_id: str,
        registry: Dict[str, TemplateDefinition],
        runtime_variables: Dict[str, str]
    ) -> List[RenderedFileVo]:
        
        order = self._resolve_order(root_template_id, registry)

        # 1. Base Context (Metadata Accumulation)
        global_variables: Dict[str, Any] = {}
        for tmpl_id in order:
            global_variables.update(registry[tmpl_id].metadata)
        # Runtime variables override everything
        global_variables.update(runtime_variables)

        candidates_map: Dict[str, List[Tuple[str, str]]] = {}

        # 2. Collect Candidates
        for tmpl_id in order:
            template = registry[tmpl_id]
            for raw_path_str, raw_content in template.files.items():
                effective_path_str = raw_path_str
                if effective_path_str.endswith(".jinja"):
                    effective_path_str = effective_path_str[:-6] 

                try:
                    # Determine destination path based on global vars (e.g. root_package)
                    dest_path = self._render_string(effective_path_str, global_variables)
                except Exception as e:
                    raise TemplateRenderingError(
                        template_id=tmpl_id, 
                        reason=f"Path render failed for '{raw_path_str}': {e}"
                    )
                
                if dest_path not in candidates_map:
                    candidates_map[dest_path] = []
                candidates_map[dest_path].append((tmpl_id, raw_content))

        # 3. Process & Merge
        results: List[RenderedFileVo] = []

        for dest_path, candidates in candidates_map.items():
            # Context is reset for each file, starting with globals
            file_context = global_variables.copy()
            selected_content: Optional[str] = None
            selected_source_id: Optional[str] = None

            for tmpl_id, raw_content in candidates:
                # --- PARSING LOGIC ---
                try:
                    strategy, local_vars, body_content = self._parse_front_matter(raw_content)
                except yaml.YAMLError as e:
                    raise TemplateRenderingError(
                        template_id=tmpl_id, 
                        reason=f"Invalid YAML Front Matter in file mapping to '{dest_path}': {e}"
                    )
                
                if local_vars:
                    self._deep_update(file_context, local_vars)

                if strategy == "replace":
                    selected_content = body_content
                    selected_source_id = tmpl_id
                elif strategy == "add":
                    # Content is ignored, only vars are injected into context
                    pass
                else:
                    # Default: Implicit replace if no strategy defined
                    selected_content = body_content
                    selected_source_id = tmpl_id

            if selected_content is not None:
                try:
                    # Render final content using the fully built context
                    final_content = self._render_string(selected_content, file_context)
                    
                    results.append(RenderedFileVo(
                        relative_path=dest_path, # Path is already a Path object or string
                        content=final_content
                    ))
                except Exception as e:
                    raise TemplateRenderingError(
                        template_id=selected_source_id or "unknown", 
                        reason=f"Content render failed for '{dest_path}': {e}"
                    )
            
        return results

    def _parse_front_matter(self, content: str) -> Tuple[str, Dict[str, Any], str]:
        """
        Parses 'Front Matter' style metadata.
        Format:
        ---
        key: value
        ---
        Body content...
        """
        # Regex to find the Front Matter block. 
        # Matches start of string (^) followed by ---, 
        # then non-greedy match of anything (.+?), 
        # then closing --- followed by optional newline.
        # flags=re.DOTALL allows dot to match newlines.
        front_matter_pattern = re.compile(r"^---\s*\n(.+?)\n---\s*(.*)$", re.DOTALL)
        
        match = front_matter_pattern.match(content)
        
        if match:
            yaml_block = match.group(1)
            body = match.group(2)
            
            # Explicitly parse YAML. If it fails, it raises YAMLError which we catch in compose
            meta = yaml.safe_load(yaml_block) or {}
            
            # Extract Strategy
            strategy = meta.pop("scaffolding", "replace")
            
            # Everything else is variables
            variables = meta
            # Support explicit 'variables' key merge if present
            if "variables" in meta and isinstance(meta["variables"], dict):
                explicit_vars = meta.pop("variables")
                self._deep_update(variables, explicit_vars)
                
            return strategy, variables, body
        else:
            # Fallback: No Front Matter -> Standard file, no vars, implicit replace
            return "replace", {}, content

    def _resolve_order(self, root_id: str, registry: Dict[str, TemplateDefinition]) -> List[str]:
        resolved: List[str] = []
        visited: Set[str] = set()
        
        def visit(node_id: str):
            if node_id in visited: return
            if node_id not in registry: return 
            template = registry[node_id]
            for dep in template.dependencies: visit(dep)
            visited.add(node_id)
            resolved.append(node_id)
            
        visit(root_id)
        return resolved

    def _render_string(self, text: str, variables: Dict[str, Any]) -> str:
        try:
            return self._jinja_env.from_string(text).render(**variables)
        except TemplateError as e:
            raise e

    def _deep_update(self, target: dict, source: dict):
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value