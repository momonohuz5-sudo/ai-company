"""Image organization for work and scene structure."""

from pathlib import Path
from typing import List
import shutil

from .storage import Storage
from .logger import PrivacySafeLogger


class Organizer:
    """Organizes generated images by work and scene."""

    def __init__(self, output_base_dir: Path, logger: PrivacySafeLogger):
        """Initialize organizer.

        Args:
            output_base_dir: Base output directory
            logger: Logger instance
        """
        self.output_base_dir = output_base_dir
        self.logger = logger

    def organize_output(
        self,
        work_id: str,
        scene_no: int,
        source_files: List[Path],
        move: bool = False
    ) -> List[Path]:
        """Organize output images for a scene.

        Args:
            work_id: Work identifier
            scene_no: Scene number
            source_files: List of source image files
            move: If True, move files; if False, copy files

        Returns:
            List of organized file paths
        """
        scene_dir = self.output_base_dir / work_id / "raw" / f"scene_{scene_no:03d}"
        Storage.ensure_dir(scene_dir)

        organized_files = []

        for idx, source_file in enumerate(source_files):
            if not source_file.exists():
                self.logger.warning(f"Source file not found: {source_file}")
                continue

            dest_file = scene_dir / f"{source_file.stem}_{idx:04d}{source_file.suffix}"

            try:
                if move:
                    shutil.move(str(source_file), str(dest_file))
                    operation = "moved"
                else:
                    shutil.copy2(str(source_file), str(dest_file))
                    operation = "copied"

                organized_files.append(dest_file)
                self.logger.log_file_operation(operation, dest_file, success=True)

            except Exception as e:
                self.logger.error(
                    f"Failed to organize {source_file.name}: {type(e).__name__}"
                )

        self.logger.info(
            f"Organized {len(organized_files)} images for {work_id}/scene_{scene_no:03d}"
        )

        return organized_files

    def get_scene_images(self, work_id: str, scene_no: int) -> List[Path]:
        """Get all images for a scene.

        Args:
            work_id: Work identifier
            scene_no: Scene number

        Returns:
            List of image file paths
        """
        scene_dir = self.output_base_dir / work_id / "raw" / f"scene_{scene_no:03d}"

        if not scene_dir.exists():
            return []

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        images = [
            f for f in scene_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        return sorted(images)

    def get_work_images(self, work_id: str) -> List[Path]:
        """Get all images for a work (all scenes).

        Args:
            work_id: Work identifier

        Returns:
            List of image file paths
        """
        raw_dir = self.output_base_dir / work_id / "raw"

        if not raw_dir.exists():
            return []

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        images = []

        for scene_dir in sorted(raw_dir.iterdir()):
            if scene_dir.is_dir():
                scene_images = [
                    f for f in scene_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in image_extensions
                ]
                images.extend(sorted(scene_images))

        return images
