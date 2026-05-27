"""Tests for storage module."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.storage import Storage


class TestStorage:
    """Test Storage class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    def test_save_and_load_json(self, temp_dir):
        """Test saving and loading JSON files."""
        test_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 123}

        Storage.save_json(test_file, test_data)
        assert test_file.exists()

        loaded_data = Storage.load_json(test_file)
        assert loaded_data == test_data

    def test_file_exists(self, temp_dir):
        """Test file existence check."""
        test_file = temp_dir / "test.json"

        assert not Storage.file_exists(test_file)

        Storage.save_json(test_file, {})
        assert Storage.file_exists(test_file)

    def test_ensure_dir(self, temp_dir):
        """Test directory creation."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        assert not nested_dir.exists()

        Storage.ensure_dir(nested_dir)
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_list_json_files(self, temp_dir):
        """Test listing JSON files."""
        Storage.save_json(temp_dir / "file1.json", {})
        Storage.save_json(temp_dir / "file2.json", {})
        (temp_dir / "file3.txt").touch()

        json_files = Storage.list_json_files(temp_dir)

        assert len(json_files) == 2
        assert all(f.suffix == ".json" for f in json_files)

    def test_atomic_write(self, temp_dir):
        """Test atomic write (no partial files left on error)."""
        test_file = temp_dir / "test.json"

        Storage.save_json(test_file, {"data": "first"})
        assert Storage.load_json(test_file) == {"data": "first"}

        Storage.save_json(test_file, {"data": "second"})
        assert Storage.load_json(test_file) == {"data": "second"}

        tmp_files = list(temp_dir.glob("*.tmp"))
        assert len(tmp_files) == 0
