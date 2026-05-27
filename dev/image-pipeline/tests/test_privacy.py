"""Privacy validation tests - CRITICAL for security."""

import pytest
from pathlib import Path
import tempfile
import shutil
import logging

from src.prompt_manager import PromptManager
from src.scene_planner import ScenePlanner
from src.logger import get_logger
from src.storage import Storage


class TestPrivacy:
    """Test privacy safeguards."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def setup_dirs(self, temp_dir):
        """Set up test directories."""
        blocks_dir = temp_dir / "blocks"
        private_dir = temp_dir / "private"
        logs_dir = temp_dir / "logs"

        for block_type in ["quality", "character", "setting", "lighting", "camera"]:
            Storage.ensure_dir(blocks_dir / block_type)

        Storage.ensure_dir(private_dir / "blocks")
        Storage.ensure_dir(logs_dir)

        return blocks_dir, private_dir, logs_dir

    def test_private_block_not_read(self, temp_dir, setup_dirs, caplog):
        """CRITICAL: Verify private block content is never read."""
        blocks_dir, private_dir, logs_dir = setup_dirs
        logger = get_logger("test", logs_dir)

        pm = PromptManager(blocks_dir, private_dir, logger)

        ref = pm.create_private_ref("private", "test_private_001")

        private_file = private_dir / "blocks" / f"{ref.block_id}.json"
        SECRET_CONTENT = "THIS_IS_SECRET_CONTENT_SHOULD_NEVER_APPEAR_IN_LOGS"
        Storage.save_json(private_file, {"content": SECRET_CONTENT})

        caplog.set_level(logging.DEBUG)

        exists = pm.validate_block_exists(ref.block_id, "private")
        assert exists is True

        assert SECRET_CONTENT not in caplog.text
        assert "OPAQUE" not in caplog.text or "private" in caplog.text.lower()

    def test_scene_validation_no_content_read(self, temp_dir, setup_dirs, caplog):
        """CRITICAL: Verify scene validation doesn't read private content."""
        blocks_dir, private_dir, logs_dir = setup_dirs
        logger = get_logger("test", logs_dir)

        pm = PromptManager(blocks_dir, private_dir, logger)

        for block_type in ["quality", "character", "setting", "lighting", "camera"]:
            pm.create_block(
                block_type,
                f"test {block_type} content",
                parameters={"steps": 30} if block_type == "quality" else {}
            )

        private_ref = pm.create_private_ref("private", "private_001")
        negative_ref = pm.create_private_ref("negative", "negative_001")

        SECRET_PRIVATE = "SECRET_PRIVATE_CONTENT"
        SECRET_NEGATIVE = "SECRET_NEGATIVE_CONTENT"

        Storage.save_json(
            private_dir / "blocks" / f"{private_ref.block_id}.json",
            {"content": SECRET_PRIVATE}
        )
        Storage.save_json(
            private_dir / "blocks" / f"{negative_ref.block_id}.json",
            {"content": SECRET_NEGATIVE}
        )

        scenes_dir = temp_dir / "scenes"
        output_dir = temp_dir / "output"

        sp = ScenePlanner(scenes_dir, output_dir, pm, logger)

        caplog.set_level(logging.DEBUG)

        quality_blocks = pm.list_blocks("quality")
        character_blocks = pm.list_blocks("character")
        setting_blocks = pm.list_blocks("setting")
        lighting_blocks = pm.list_blocks("lighting")
        camera_blocks = pm.list_blocks("camera")

        scene_config = {
            "scene_no": 1,
            "quality_id": quality_blocks[0].block_id,
            "character_id": character_blocks[0].block_id,
            "setting_id": setting_blocks[0].block_id,
            "lighting_id": lighting_blocks[0].block_id,
            "camera_id": camera_blocks[0].block_id,
            "private_id": private_ref.block_id,
            "negative_id": negative_ref.block_id
        }

        scenes = sp.create_scene_plan("test_work", [scene_config])

        assert len(scenes) == 1

        assert SECRET_PRIVATE not in caplog.text
        assert SECRET_NEGATIVE not in caplog.text

    def test_error_messages_no_private_content(self, temp_dir, setup_dirs):
        """CRITICAL: Verify error messages don't expose private content."""
        blocks_dir, private_dir, logs_dir = setup_dirs
        logger = get_logger("test", logs_dir)

        pm = PromptManager(blocks_dir, private_dir, logger)

        exists = pm.validate_block_exists("nonexistent_private", "private")
        assert exists is False
