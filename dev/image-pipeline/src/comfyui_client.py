"""ComfyUI API integration with privacy-safe logging and dry-run mode."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import time

from .models import Scene
from .logger import PrivacySafeLogger


class ComfyUIClient:
    """Client for ComfyUI REST API with dry-run mode."""

    def __init__(
        self,
        endpoint: str,
        timeout: int,
        dry_run: bool,
        logger: PrivacySafeLogger,
        api_key: Optional[str] = None
    ):
        """Initialize ComfyUI client.

        Args:
            endpoint: ComfyUI API endpoint URL
            timeout: Request timeout in seconds
            dry_run: Dry-run mode (no actual API calls)
            logger: Logger instance
            api_key: Optional API key for authentication
        """
        self.endpoint = endpoint.rstrip('/')
        self.timeout = timeout
        self.dry_run = dry_run
        self.logger = logger
        self.api_key = api_key

    def submit_scene(self, scene: Scene) -> Optional[str]:
        """Submit a single scene to ComfyUI.

        Args:
            scene: Scene to submit

        Returns:
            Job ID if submitted (None in dry-run mode)

        Privacy Note:
            Logs only scene_no and block IDs, never content.
        """
        payload = self._build_payload(scene)

        if self.dry_run:
            self.logger.log_api_submission(scene.scene_no, dry_run=True)
            self.logger.debug(
                f"DRY-RUN: Payload structure for scene {scene.scene_no:03d}: "
                f"quality={scene.quality_id}, character={scene.character_id}, "
                f"setting={scene.setting_id}, lighting={scene.lighting_id}, "
                f"camera={scene.camera_id}, private=OPAQUE, negative=OPAQUE, "
                f"seed={scene.seed}"
            )
            return None

        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.endpoint}/api/queue",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()
            job_id = result.get("job_id") or result.get("prompt_id")

            self.logger.log_api_submission(scene.scene_no, job_id)

            return job_id

        except requests.RequestException as e:
            self.logger.error(
                f"Failed to submit scene {scene.scene_no:03d}: {type(e).__name__}"
            )
            raise

    def submit_batch(self, scenes: List[Scene]) -> List[Optional[str]]:
        """Submit multiple scenes to ComfyUI.

        Args:
            scenes: List of scenes to submit

        Returns:
            List of job IDs (None for failed submissions or dry-run)

        Privacy Note:
            Each scene submission is privacy-safe.
        """
        job_ids = []

        for scene in scenes:
            try:
                job_id = self.submit_scene(scene)
                job_ids.append(job_id)
            except Exception as e:
                self.logger.error(
                    f"Scene {scene.scene_no:03d} submission failed: {type(e).__name__}"
                )
                job_ids.append(None)

        total = len(scenes)
        success = sum(1 for jid in job_ids if jid is not None or self.dry_run)

        self.logger.info(f"Batch submission completed: {success}/{total} scenes")

        return job_ids

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status from ComfyUI.

        Args:
            job_id: ComfyUI job ID

        Returns:
            Job status dict

        Raises:
            requests.RequestException: If API call fails
        """
        if self.dry_run:
            self.logger.debug(f"DRY-RUN: Would check status for job {job_id}")
            return {"status": "pending", "job_id": job_id}

        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(
                f"{self.endpoint}/api/queue/{job_id}",
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Failed to get job status {job_id}: {type(e).__name__}")
            raise

    def _build_payload(self, scene: Scene) -> Dict[str, Any]:
        """Build API payload for scene.

        Args:
            scene: Scene to build payload for

        Returns:
            Payload dict

        Privacy Note:
            This is a placeholder. Actual implementation depends on ComfyUI workflow.
            Real implementation would load private blocks from disk (outside tool scope).
        """
        return {
            "work_id": scene.work_id,
            "scene_no": scene.scene_no,
            "quality_id": scene.quality_id,
            "character_id": scene.character_id,
            "setting_id": scene.setting_id,
            "lighting_id": scene.lighting_id,
            "camera_id": scene.camera_id,
            "private_id": scene.private_id,
            "negative_id": scene.negative_id,
            "seed": scene.seed,
            "output_dir": scene.output_dir
        }
