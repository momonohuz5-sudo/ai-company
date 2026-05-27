"""ComfyUI API integration with privacy-safe logging and dry-run mode."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import time
import uuid

from .models import Scene, PromptBlock
from .logger import PrivacySafeLogger
from .storage import Storage


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

    def submit_scene_with_workflow(self, scene: Scene, workflow: Dict[str, Any]) -> Optional[str]:
        """Submit a single scene to ComfyUI with workflow.

        Args:
            scene: Scene to submit
            workflow: Complete ComfyUI workflow

        Returns:
            Job ID if submitted (None in dry-run mode)

        Privacy Note:
            Logs only scene_no and block IDs, never content.
        """
        client_id = str(uuid.uuid4())

        payload = {
            "prompt": workflow,
            "client_id": client_id
        }

        if self.dry_run:
            self.logger.log_api_submission(scene.scene_no, dry_run=True)
            self.logger.debug(
                f"DRY-RUN: Would submit scene {scene.scene_no:03d} with workflow to {self.endpoint}/prompt"
            )
            return f"dry_run_{scene.scene_no}"

        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.endpoint}/prompt",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            result = response.json()
            prompt_id = result.get("prompt_id")

            self.logger.log_api_submission(scene.scene_no, prompt_id)

            return prompt_id

        except requests.RequestException as e:
            self.logger.error(
                f"Failed to submit scene {scene.scene_no:03d}: {type(e).__name__}"
            )
            raise

    def submit_batch_with_workflows(
        self,
        scenes: List[Scene],
        workflows: List[Dict[str, Any]]
    ) -> List[Optional[str]]:
        """Submit multiple scenes to ComfyUI with workflows.

        Args:
            scenes: List of scenes to submit
            workflows: List of workflows (one per scene)

        Returns:
            List of job IDs (None for failed submissions)

        Privacy Note:
            Each scene submission is privacy-safe.
        """
        if len(scenes) != len(workflows):
            raise ValueError(f"Scene count ({len(scenes)}) must match workflow count ({len(workflows)})")

        job_ids = []

        for scene, workflow in zip(scenes, workflows):
            try:
                job_id = self.submit_scene_with_workflow(scene, workflow)
                job_ids.append(job_id)

                if not self.dry_run:
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(
                    f"Scene {scene.scene_no:03d} submission failed: {type(e).__name__}"
                )
                job_ids.append(None)

        total = len(scenes)
        success = sum(1 for jid in job_ids if jid is not None)

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

    def check_connection(self) -> bool:
        """Check if ComfyUI server is reachable.

        Returns:
            True if server is reachable
        """
        if self.dry_run:
            self.logger.info("DRY-RUN: Skipping connection check")
            return True

        try:
            response = requests.get(
                f"{self.endpoint}/system_stats",
                timeout=5
            )
            response.raise_for_status()
            self.logger.info(f"✓ Connected to ComfyUI at {self.endpoint}")
            return True
        except requests.RequestException as e:
            self.logger.warning(
                f"Cannot connect to ComfyUI at {self.endpoint}: {type(e).__name__}"
            )
            return False
