import logging
from pathlib import Path
from typing import Any

import yaml

from ...domain import ConfigVo, ProjectConfig, ScannerConfig

logger = logging.getLogger(__name__)


class YamlConfigLoader:
    """
    Driven Adapter: Reads configuration from physical YAML files.
    """

    def load(self, override_path: Path | None = None) -> ConfigVo:
        """
        Loads the configuration using Upward Discovery.
        """
        config_path = override_path or self._discover_config_file()
        if not config_path or not config_path.exists():
            return ConfigVo()

        try:
            raw_text = config_path.read_text(encoding="utf-8")
            data: dict[str, Any] = yaml.safe_load(raw_text) or {}
            return self._parse_dict(data, config_path)
        except yaml.YAMLError as e:
            logger.warning("Invalid YAML in %s: %s. Using defaults.", config_path, e)
            return ConfigVo()
        except OSError as e:
            logger.warning("Cannot read config %s: %s. Using defaults.", config_path, e)
            return ConfigVo()

    def _discover_config_file(self) -> Path | None:
        """
        Searches for config file starting from CWD and going upwards.
        """
        current = Path.cwd().resolve()
        root = Path(current.anchor)

        while True:
            candidates = [
                current / "docs" / "dddguard" / "config.yaml",
                current / "dddguard" / "config.yaml",
                current / "config.yaml",
            ]

            for path in candidates:
                if path.exists() and path.is_file():
                    return path

            if current == root:
                break
            current = current.parent

        return None

    def _parse_dict(self, data: dict[str, Any], config_file_path: Path) -> ConfigVo:
        """
        Maps raw dictionary to Domain Value Objects.
        Prioritizes explicit 'root_dir' in YAML.
        """
        # 1. Project Section
        proj_data: dict[str, Any] = data.get("project", {})

        # A. Resolve project root
        project_root = self._resolve_project_root(proj_data, config_file_path)

        project_conf = ProjectConfig(
            source_dir=proj_data.get("source_dir"),
            tests_dir=proj_data.get("tests_dir"),
            docs_dir=proj_data.get("docs_dir"),
            project_root=project_root,
            config_file_path=config_file_path,
        )

        # 2. Scanner Section
        scan_data: dict[str, Any] = data.get("scanner", {})
        scanner_conf = self._parse_scanner_config(scan_data)

        return ConfigVo(project=project_conf, scanner=scanner_conf)

    @staticmethod
    def _resolve_project_root(proj_data: dict[str, Any], config_file_path: Path) -> Path:
        """Determines the project root directory from config data or file location."""
        raw_root = proj_data.get("root_dir")
        if raw_root:
            return Path(raw_root).resolve()

        # Fallback: Calculate relative to config file location
        parent_name = config_file_path.parent.name
        if parent_name == "dddguard":
            grandparent = config_file_path.parents[1]
            if grandparent.name == "docs":
                return config_file_path.parents[2].resolve()
            return grandparent.resolve()

        return config_file_path.parent.resolve()

    @staticmethod
    def _parse_scanner_config(scan_data: dict[str, Any]) -> ScannerConfig:
        """Builds ScannerConfig from the 'scanner' section of YAML data."""
        kwargs: dict[str, Any] = {}

        if "exclude_dirs" in scan_data:
            kwargs["exclude_dirs"] = frozenset(scan_data["exclude_dirs"])

        if "ignore_files" in scan_data:
            kwargs["ignore_files"] = frozenset(scan_data["ignore_files"])

        if "max_file_size_bytes" in scan_data:
            kwargs["max_file_size_bytes"] = scan_data["max_file_size_bytes"]

        return ScannerConfig(**kwargs)
