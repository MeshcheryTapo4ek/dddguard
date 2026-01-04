from dataclasses import dataclass
from pathlib import Path
from typing import List

from dddguard.scanner import ScannerController, ScanResponseSchema

from ....app import IScannerGateway
from ....domain import ScannedNodeVo, ScannedImportVo
from .errors import ScannerIntegrationError


@dataclass(frozen=True, kw_only=True, slots=True)
class ScannerAcl(IScannerGateway):
    """
    Driven Adapter (ACL): Anti-Corruption Layer.
    1. Calls ScannerController (Driving Port of Scanner).
    2. Translates ScanResponseSchema (DTO) -> List[ScannedNodeVo] (Domain).
    3. Translates ScannerAppError -> ScannerIntegrationError.
    """

    controller: ScannerController

    def get_project_nodes(self, root_path: Path) -> List[ScannedNodeVo]:
        try:
            # 1. Call External System
            response: ScanResponseSchema = self.controller.scan_project(
                target_path=root_path, scan_all=False, show_root=True, show_shared=True
            )

            # 2. Translate Data (DTO -> Domain)
            return self._map_schema_to_domain(response.dependency_graph)

        except Exception as e:
            raise ScannerIntegrationError(original_error=e) from e

    def _map_schema_to_domain(self, graph_dict: dict) -> List[ScannedNodeVo]:
        """
        Parses the hierarchical dictionary from the Schema into flat Node VOs.
        Structure: {context: {layer: [ {module, type, imports: []} ] }}
        """
        nodes: List[ScannedNodeVo] = []

        for context_name, layers in graph_dict.items():
            for layer_name, modules in layers.items():
                for mod_data in modules:
                    # Map Imports
                    mapped_imports = []
                    for imp in mod_data.get("imports", []):
                        mapped_imports.append(
                            ScannedImportVo(
                                target_module=imp.get("module", ""),
                                target_context=imp.get("context"),
                                target_layer=imp.get("layer"),
                            )
                        )

                    # Create Local Domain Object
                    nodes.append(
                        ScannedNodeVo(
                            module_path=mod_data.get("module", ""),
                            context=context_name,
                            layer=layer_name,
                            imports=mapped_imports,
                        )
                    )
        return nodes