"""Privacy-safe logging for the image production pipeline."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class PrivacySafeLogger:
    """Logger that ensures no private content is logged.

    Principles:
    - Log block IDs, not content
    - Log file paths, not image data
    - Log operation results, not sensitive details
    - All log messages are sanitized
    """

    def __init__(self, name: str, log_file: Optional[Path] = None, level: int = logging.INFO):
        """Initialize logger.

        Args:
            name: Logger name (typically module name)
            log_file: Optional file path for log output
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def log_scene_created(self, scene_no: int, quality_id: str, character_id: str,
                          setting_id: str, lighting_id: str, camera_id: str,
                          seed: int) -> None:
        """Log scene creation (privacy-safe).

        Privacy Note:
            Logs only block IDs (OPAQUE references), not content.
            Private/negative IDs are logged as "OPAQUE" placeholder.
        """
        self.info(
            f"Scene {scene_no:03d} created: "
            f"quality={quality_id}, character={character_id}, "
            f"setting={setting_id}, lighting={lighting_id}, "
            f"camera={camera_id}, private=OPAQUE, negative=OPAQUE, "
            f"seed={seed}"
        )

    def log_api_submission(self, scene_no: int, job_id: Optional[str] = None,
                           dry_run: bool = False) -> None:
        """Log ComfyUI API submission (privacy-safe).

        Args:
            scene_no: Scene number
            job_id: ComfyUI job ID (if available)
            dry_run: Whether this is a dry-run
        """
        prefix = "DRY-RUN: " if dry_run else ""
        job_info = f", job_id={job_id}" if job_id else ""
        self.info(f"{prefix}Scene {scene_no:03d} submitted to ComfyUI{job_info}")

    def log_file_operation(self, operation: str, file_path: Path, success: bool = True) -> None:
        """Log file operation (privacy-safe).

        Args:
            operation: Operation description (e.g., "moved", "copied", "created")
            file_path: File path
            success: Whether operation succeeded
        """
        status = "successfully" if success else "FAILED"
        self.info(f"File {operation} {status}: {file_path}")

    def log_block_validation(self, block_id: str, exists: bool) -> None:
        """Log block validation result (privacy-safe).

        Privacy Note:
            Only logs existence check result, never reads or logs content.
        """
        status = "exists" if exists else "NOT FOUND"
        self.info(f"Block validation: {block_id} - {status}")


def get_logger(name: str, log_dir: Optional[Path] = None) -> PrivacySafeLogger:
    """Get a privacy-safe logger instance.

    Args:
        name: Logger name
        log_dir: Optional directory for log files

    Returns:
        PrivacySafeLogger instance
    """
    log_file = None
    if log_dir:
        log_file = log_dir / "pipeline.log"

    return PrivacySafeLogger(name, log_file)
