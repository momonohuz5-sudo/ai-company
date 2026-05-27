"""Metadata export for works."""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .models import Work, Scene
from .storage import Storage
from .logger import PrivacySafeLogger


class MetadataExporter:
    """Exports work metadata without private content."""

    def __init__(self, logger: PrivacySafeLogger):
        """Initialize metadata exporter.

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def export_metadata(
        self,
        work: Work,
        scenes: List[Scene],
        approved_count: int,
        output_path: Path
    ) -> Dict[str, Any]:
        """Export work metadata to JSON.

        Args:
            work: Work instance
            scenes: List of scenes
            approved_count: Number of approved images
            output_path: Output file path

        Returns:
            Metadata dict

        Privacy Note:
            Only exports block IDs, never content.
        """
        blocks_used = self._collect_blocks_used(scenes)

        metadata = {
            "work_id": work.work_id,
            "title": work.title,
            "description": work.description,
            "created_at": work.created_at,
            "status": work.status,
            "scene_count": len(scenes),
            "image_count": len(scenes),
            "approved_count": approved_count,
            "blocks_used": blocks_used,
            "exported_at": datetime.now().isoformat()
        }

        Storage.save_json(output_path, metadata)

        self.logger.info(f"Metadata exported: {output_path.name}")

        return metadata

    def _collect_blocks_used(self, scenes: List[Scene]) -> Dict[str, List[str]]:
        """Collect unique block IDs used across scenes.

        Args:
            scenes: List of scenes

        Returns:
            Dict of block_type -> list of unique block IDs

        Privacy Note:
            Private/negative block IDs are collected, but marked as OPAQUE.
        """
        quality_ids = set()
        character_ids = set()
        setting_ids = set()
        lighting_ids = set()
        camera_ids = set()

        for scene in scenes:
            quality_ids.add(scene.quality_id)
            character_ids.add(scene.character_id)
            setting_ids.add(scene.setting_id)
            lighting_ids.add(scene.lighting_id)
            camera_ids.add(scene.camera_id)

        return {
            "quality": sorted(quality_ids),
            "character": sorted(character_ids),
            "setting": sorted(setting_ids),
            "lighting": sorted(lighting_ids),
            "camera": sorted(camera_ids),
            "private": ["OPAQUE"],
            "negative": ["OPAQUE"]
        }
