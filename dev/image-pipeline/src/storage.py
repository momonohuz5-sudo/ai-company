"""File-based storage operations with privacy and Windows compatibility."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class Storage:
    """Handles JSON file operations with atomic writes and Windows compatibility."""

    @staticmethod
    def ensure_dir(path: Path) -> None:
        """Create directory if it doesn't exist.

        Args:
            path: Directory path to create
        """
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_json(path: Path, data: Dict[str, Any], indent: int = 2) -> None:
        """Save data to JSON file with atomic write.

        Args:
            path: File path to write
            data: Data to save
            indent: JSON indentation level

        Privacy Note:
            This method does not inspect data content.
            Caller is responsible for ensuring no private content is passed.
        """
        Storage.ensure_dir(path.parent)

        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=path.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp_file:
            json.dump(data, tmp_file, indent=indent, ensure_ascii=False)
            tmp_path = Path(tmp_file.name)

        tmp_path.replace(path)

    @staticmethod
    def load_json(path: Path) -> Dict[str, Any]:
        """Load data from JSON file.

        Args:
            path: File path to read

        Returns:
            Loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with path.open('r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def list_json_files(directory: Path, pattern: str = "*.json") -> List[Path]:
        """List JSON files in a directory.

        Args:
            directory: Directory to search
            pattern: File pattern to match

        Returns:
            List of matching file paths
        """
        if not directory.exists():
            return []

        return sorted(directory.glob(pattern))

    @staticmethod
    def file_exists(path: Path) -> bool:
        """Check if file exists without reading its content.

        Args:
            path: File path to check

        Returns:
            True if file exists

        Privacy Note:
            This method only checks file existence, never reads content.
        """
        return path.exists() and path.is_file()

    @staticmethod
    def create_marker_file(path: Path) -> None:
        """Create an empty marker file (for private block refs).

        Args:
            path: File path to create

        Privacy Note:
            Creates empty file as existence marker only.
            Does not write any content.
        """
        Storage.ensure_dir(path.parent)
        path.touch()
