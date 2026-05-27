"""Approval workflow for image selection."""

from pathlib import Path
from typing import List
import shutil

from .storage import Storage
from .logger import PrivacySafeLogger


class ApprovalManager:
    """Manages image approval/rejection workflow."""

    def __init__(self, output_base_dir: Path, logger: PrivacySafeLogger):
        """Initialize approval manager.

        Args:
            output_base_dir: Base output directory
            logger: Logger instance
        """
        self.output_base_dir = output_base_dir
        self.logger = logger

    def mark_approved(self, work_id: str, image_path: Path) -> Path:
        """Mark an image as approved.

        Args:
            work_id: Work identifier
            image_path: Path to image file

        Returns:
            Path to approved image

        Raises:
            FileNotFoundError: If image doesn't exist
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        approved_dir = self.output_base_dir / work_id / "approved"
        Storage.ensure_dir(approved_dir)

        dest_path = approved_dir / image_path.name

        shutil.copy2(str(image_path), str(dest_path))

        self.logger.log_file_operation("approved", dest_path, success=True)
        self.logger.info(f"Image approved: {image_path.name}")

        return dest_path

    def mark_rejected(self, work_id: str, image_path: Path) -> Path:
        """Mark an image as rejected.

        Args:
            work_id: Work identifier
            image_path: Path to image file

        Returns:
            Path to rejected image

        Raises:
            FileNotFoundError: If image doesn't exist
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        rejected_dir = self.output_base_dir / work_id / "rejected"
        Storage.ensure_dir(rejected_dir)

        dest_path = rejected_dir / image_path.name

        shutil.move(str(image_path), str(dest_path))

        self.logger.log_file_operation("rejected", dest_path, success=True)
        self.logger.info(f"Image rejected: {image_path.name}")

        return dest_path

    def list_approved(self, work_id: str) -> List[Path]:
        """List approved images for a work.

        Args:
            work_id: Work identifier

        Returns:
            List of approved image paths
        """
        approved_dir = self.output_base_dir / work_id / "approved"

        if not approved_dir.exists():
            return []

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        images = [
            f for f in approved_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        return sorted(images)

    def list_rejected(self, work_id: str) -> List[Path]:
        """List rejected images for a work.

        Args:
            work_id: Work identifier

        Returns:
            List of rejected image paths
        """
        rejected_dir = self.output_base_dir / work_id / "rejected"

        if not rejected_dir.exists():
            return []

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        images = [
            f for f in rejected_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        return sorted(images)

    def list_pending(self, work_id: str) -> List[Path]:
        """List pending (not yet approved/rejected) images for a work.

        Args:
            work_id: Work identifier

        Returns:
            List of pending image paths
        """
        raw_dir = self.output_base_dir / work_id / "raw"

        if not raw_dir.exists():
            return []

        approved = {img.name for img in self.list_approved(work_id)}
        rejected = {img.name for img in self.list_rejected(work_id)}

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        pending = []

        for scene_dir in raw_dir.iterdir():
            if scene_dir.is_dir():
                for img in scene_dir.iterdir():
                    if (
                        img.is_file()
                        and img.suffix.lower() in image_extensions
                        and img.name not in approved
                        and img.name not in rejected
                    ):
                        pending.append(img)

        return sorted(pending)
