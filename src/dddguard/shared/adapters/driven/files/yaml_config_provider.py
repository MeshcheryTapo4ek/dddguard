import yaml
from pathlib import Path
from typing import Optional

from ....domain import ConfigVo, ProjectConfig, ScannerConfig


class YamlConfigLoader:
    """
    Driven Adapter: Reads configuration from physical YAML files.
    """

    def load(self, override_path: Optional[Path] = None) -> ConfigVo:
        """
        Loads the configuration using Upward Discovery.
        """
        config_path = override_path if override_path else self._discover_config_file()

        # If not found, default to CWD
        if not config_path or not config_path.exists():
            return ConfigVo(project=ProjectConfig(project_root=Path.cwd()))

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return self._parse_dict(data, config_path)
        except Exception as e:
            print(
                f"WARN: Failed to load config from {config_path}: {e}. Using defaults."
            )
            return ConfigVo(project=ProjectConfig(project_root=Path.cwd()))

    def _discover_config_file(self) -> Optional[Path]:
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

    def _parse_dict(self, data: dict, config_file_path: Path) -> ConfigVo:
        """
        Maps raw dictionary to Domain Value Objects.
        Prioritizes explicit 'root_dir' in YAML.
        """
        # 1. Project Section
        proj_data = data.get("project", {})

        # A. Check for explicit absolute root in YAML
        raw_root = proj_data.get("root_dir")
        if raw_root:
            project_root = Path(raw_root).resolve()
        else:
            # B. Fallback: Calculate relative to config file
            # Default assumption: config is deep in docs/dddguard/ -> root is ../../
            # If config is in root/, this might need adjustment, but generally works if config is in a subdir
            # Let's be smarter: if config is in docs/dddguard, go up 2. If in root, go up 0.
            if config_file_path.parent.name == "dddguard":
                project_root = config_file_path.parents[1].resolve()
                if config_file_path.parents[1].name == "docs":
                    project_root = config_file_path.parents[2].resolve()
            else:
                # Default safe fallback
                project_root = config_file_path.parent.resolve()

        project_conf = ProjectConfig(
            source_dir=proj_data.get("source_dir", "src"),
            tests_dir=proj_data.get("tests_dir", "tests"),
            docs_dir=proj_data.get("docs_dir", "docs"),
            project_root=project_root,
            config_file_path=config_file_path,
        )

        # 2. Scanner Section
        scan_data = data.get("scanner", {})

        exclude_dirs = set(scan_data.get("exclude_dirs", []))
        if not exclude_dirs:
            exclude_dirs = ScannerConfig().exclude_dirs

        ignore_files = set(scan_data.get("ignore_files", []))
        if not ignore_files:
            ignore_files = ScannerConfig().ignore_files

        scanner_conf = ScannerConfig(
            exclude_dirs=exclude_dirs, ignore_files=ignore_files
        )

        return ConfigVo(project=project_conf, scanner=scanner_conf)
