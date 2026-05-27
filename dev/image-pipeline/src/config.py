"""Configuration loader for the image production pipeline."""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class Config:
    """Application configuration with defaults and validation."""

    DEFAULT_CONFIG = {
        "comfyui": {
            "endpoint": "http://localhost:8188",
            "api_key": None,
            "timeout": 300,
            "dry_run": True
        },
        "paths": {
            "data_dir": "data",
            "output_dir": "output",
            "logs_dir": "logs",
            "private_dir": "data/private"
        },
        "generation": {
            "default_seed_start": 1000,
            "seed_increment": 1
        },
        "packaging": {
            "renumber_start": 1,
            "sample_count": 5,
            "create_zip": True,
            "zip_compression": "deflate"
        },
        "privacy": {
            "log_private_content": False,
            "log_block_ids_only": True
        }
    }

    def __init__(self, config_path: Optional[Path] = None, root_dir: Optional[Path] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config YAML file
            root_dir: Root directory for resolving relative paths (defaults to config parent)
        """
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path and config_path.exists():
            with config_path.open('r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
                self._merge_config(user_config)

        if root_dir is None and config_path:
            root_dir = config_path.parent.parent
        elif root_dir is None:
            root_dir = Path.cwd()

        self.root_dir = root_dir
        self._resolve_paths()

    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user configuration with defaults.

        Args:
            user_config: User configuration dict
        """
        for section, values in user_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values

    def _resolve_paths(self) -> None:
        """Resolve relative paths to absolute paths."""
        paths = self.config["paths"]
        for key, value in paths.items():
            if value:
                path = Path(value)
                if not path.is_absolute():
                    paths[key] = str(self.root_dir / path)

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get configuration value by nested keys.

        Args:
            *keys: Nested configuration keys
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            config.get("comfyui", "endpoint") -> "http://localhost:8188"
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def comfyui_endpoint(self) -> str:
        """Get ComfyUI API endpoint."""
        return self.get("comfyui", "endpoint")

    @property
    def comfyui_timeout(self) -> int:
        """Get ComfyUI API timeout."""
        return self.get("comfyui", "timeout")

    @property
    def dry_run(self) -> bool:
        """Get dry-run mode setting."""
        return self.get("comfyui", "dry_run")

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return Path(self.get("paths", "data_dir"))

    @property
    def output_dir(self) -> Path:
        """Get output directory path."""
        return Path(self.get("paths", "output_dir"))

    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        return Path(self.get("paths", "logs_dir"))

    @property
    def private_dir(self) -> Path:
        """Get private directory path.

        Privacy Note:
            This path is returned for validation purposes only.
            Application code should never read files from this directory.
        """
        return Path(self.get("paths", "private_dir"))

    @property
    def default_seed_start(self) -> int:
        """Get default starting seed value."""
        return self.get("generation", "default_seed_start")

    @property
    def seed_increment(self) -> int:
        """Get seed increment value."""
        return self.get("generation", "seed_increment")

    @property
    def renumber_start(self) -> int:
        """Get renumbering start value."""
        return self.get("packaging", "renumber_start")

    @property
    def sample_count(self) -> int:
        """Get sample image count."""
        return self.get("packaging", "sample_count")

    def get_work_dir(self, work_id: str) -> Path:
        """Get work-specific data directory.

        Args:
            work_id: Work ID

        Returns:
            Path to work directory
        """
        return self.data_dir / "works"

    def get_blocks_dir(self, block_type: str) -> Path:
        """Get directory for specific block type.

        Args:
            block_type: Block type (quality, character, etc.)

        Returns:
            Path to block type directory
        """
        return self.data_dir / "blocks" / block_type

    def get_scenes_dir(self) -> Path:
        """Get scenes directory path."""
        return self.data_dir / "scenes"

    def get_output_work_dir(self, work_id: str) -> Path:
        """Get output directory for specific work.

        Args:
            work_id: Work ID

        Returns:
            Path to work output directory
        """
        return self.output_dir / work_id


def load_config(config_path: Optional[Path] = None, root_dir: Optional[Path] = None) -> Config:
    """Load configuration from file or use defaults.

    Args:
        config_path: Path to config YAML file
        root_dir: Root directory for resolving relative paths

    Returns:
        Config instance
    """
    return Config(config_path, root_dir)
