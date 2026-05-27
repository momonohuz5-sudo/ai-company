"""Work/project management for the image production pipeline."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import Work
from .storage import Storage
from .logger import PrivacySafeLogger


class ProjectManager:
    """Manages work/project CRUD operations."""

    def __init__(self, works_dir: Path, logger: PrivacySafeLogger):
        """Initialize project manager.

        Args:
            works_dir: Directory for storing work files
            logger: Logger instance
        """
        self.works_dir = works_dir
        self.logger = logger
        Storage.ensure_dir(works_dir)

    def create_work(self, work_id: str, title: str, description: str = "") -> Work:
        """Create a new work.

        Args:
            work_id: Unique work identifier
            title: Work title
            description: Work description

        Returns:
            Created Work instance

        Raises:
            ValueError: If work_id already exists
        """
        work_file = self.works_dir / f"{work_id}.json"

        if work_file.exists():
            raise ValueError(f"Work already exists: {work_id}")

        work = Work.create(work_id, title, description)

        Storage.save_json(work_file, work.to_dict())

        self.logger.info(f"Work created: {work_id} - {title}")

        return work

    def get_work(self, work_id: str) -> Work:
        """Get work by ID.

        Args:
            work_id: Work identifier

        Returns:
            Work instance

        Raises:
            FileNotFoundError: If work doesn't exist
        """
        work_file = self.works_dir / f"{work_id}.json"

        if not work_file.exists():
            raise FileNotFoundError(f"Work not found: {work_id}")

        data = Storage.load_json(work_file)
        return Work.from_dict(data)

    def list_works(self) -> List[Work]:
        """List all works.

        Returns:
            List of Work instances
        """
        work_files = Storage.list_json_files(self.works_dir)
        works = []

        for work_file in work_files:
            try:
                data = Storage.load_json(work_file)
                works.append(Work.from_dict(data))
            except Exception as e:
                self.logger.error(f"Failed to load work from {work_file.name}: {type(e).__name__}")

        return sorted(works, key=lambda w: w.created_at, reverse=True)

    def update_work_status(self, work_id: str, status: str) -> Work:
        """Update work status.

        Args:
            work_id: Work identifier
            status: New status

        Returns:
            Updated Work instance

        Raises:
            FileNotFoundError: If work doesn't exist
            ValueError: If status is invalid
        """
        valid_statuses = ["planning", "generating", "reviewing", "completed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        work = self.get_work(work_id)
        work.status = status

        work_file = self.works_dir / f"{work_id}.json"
        Storage.save_json(work_file, work.to_dict())

        self.logger.info(f"Work status updated: {work_id} -> {status}")

        return work

    def work_exists(self, work_id: str) -> bool:
        """Check if work exists.

        Args:
            work_id: Work identifier

        Returns:
            True if work exists
        """
        work_file = self.works_dir / f"{work_id}.json"
        return work_file.exists()
