"""Scene planning and generation with privacy-safe validation."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import csv

from .models import Scene
from .storage import Storage
from .logger import PrivacySafeLogger
from .prompt_manager import PromptManager


class ScenePlanner:
    """Generates and manages scene plans."""

    def __init__(
        self,
        scenes_dir: Path,
        output_base_dir: Path,
        prompt_manager: PromptManager,
        logger: PrivacySafeLogger,
        default_seed_start: int = 1000,
        seed_increment: int = 1
    ):
        """Initialize scene planner.

        Args:
            scenes_dir: Directory for storing scene plans
            output_base_dir: Base output directory
            prompt_manager: PromptManager instance for validation
            logger: Logger instance
            default_seed_start: Default starting seed
            seed_increment: Seed increment for sequential scenes
        """
        self.scenes_dir = scenes_dir
        self.output_base_dir = output_base_dir
        self.prompt_manager = prompt_manager
        self.logger = logger
        self.default_seed_start = default_seed_start
        self.seed_increment = seed_increment

        Storage.ensure_dir(scenes_dir)

    def create_scene_plan(
        self,
        work_id: str,
        scenes_config: List[Dict[str, Any]],
        validate_blocks: bool = True
    ) -> List[Scene]:
        """Create scene plan from configuration.

        Args:
            work_id: Work identifier
            scenes_config: List of scene configurations
            validate_blocks: Whether to validate block existence

        Returns:
            List of Scene instances

        Raises:
            ValueError: If validation fails

        Privacy Note:
            Validation only checks block file existence, never reads content.
        """
        scenes = []

        for scene_config in scenes_config:
            scene = self._create_scene(work_id, scene_config)

            if validate_blocks:
                self._validate_scene(scene)

            scenes.append(scene)

            self.logger.log_scene_created(
                scene.scene_no,
                scene.quality_id,
                scene.character_id,
                scene.setting_id,
                scene.lighting_id,
                scene.camera_id,
                scene.seed
            )

        self.logger.info(f"Scene plan created for {work_id}: {len(scenes)} scenes")

        return scenes

    def _create_scene(self, work_id: str, config: Dict[str, Any]) -> Scene:
        """Create a single scene from config.

        Args:
            work_id: Work identifier
            config: Scene configuration dict

        Returns:
            Scene instance
        """
        scene_no = config["scene_no"]
        output_dir = str(self.output_base_dir / work_id / "raw" / f"scene_{scene_no:03d}")

        seed = config.get("seed")
        if seed is None:
            seed = self.default_seed_start + (scene_no - 1) * self.seed_increment

        return Scene(
            work_id=work_id,
            scene_no=scene_no,
            quality_id=config["quality_id"],
            character_id=config["character_id"],
            setting_id=config["setting_id"],
            lighting_id=config["lighting_id"],
            camera_id=config["camera_id"],
            private_id=config["private_id"],
            negative_id=config["negative_id"],
            seed=seed,
            output_dir=output_dir,
            status="pending"
        )

    def _validate_scene(self, scene: Scene) -> None:
        """Validate scene block references.

        Args:
            scene: Scene to validate

        Raises:
            ValueError: If any block doesn't exist

        Privacy Note:
            Only validates file existence, never reads content.
        """
        validations = [
            ("quality", scene.quality_id),
            ("character", scene.character_id),
            ("setting", scene.setting_id),
            ("lighting", scene.lighting_id),
            ("camera", scene.camera_id),
            ("private", scene.private_id),
            ("negative", scene.negative_id),
        ]

        missing = []
        for block_type, block_id in validations:
            if not self.prompt_manager.validate_block_exists(block_id, block_type):
                missing.append(f"{block_type}={block_id}")

        if missing:
            raise ValueError(
                f"Scene {scene.scene_no} validation failed. Missing blocks: {', '.join(missing)}"
            )

    def save_plan(self, work_id: str, scenes: List[Scene]) -> Path:
        """Save scene plan to JSONL file.

        Args:
            work_id: Work identifier
            scenes: List of scenes

        Returns:
            Path to saved plan file
        """
        plan_file = self.scenes_dir / f"{work_id}_scenes.jsonl"

        with plan_file.open('w', encoding='utf-8') as f:
            for scene in scenes:
                f.write(scene.to_jsonl() + '\n')

        self.logger.info(f"Scene plan saved: {plan_file.name}")

        return plan_file

    def load_plan(self, work_id: str) -> List[Scene]:
        """Load scene plan from file.

        Args:
            work_id: Work identifier

        Returns:
            List of Scene instances

        Raises:
            FileNotFoundError: If plan doesn't exist
        """
        plan_file = self.scenes_dir / f"{work_id}_scenes.jsonl"

        if not plan_file.exists():
            raise FileNotFoundError(f"Scene plan not found for work: {work_id}")

        scenes = []
        with plan_file.open('r', encoding='utf-8') as f:
            for line in f:
                import json
                data = json.loads(line.strip())
                scenes.append(Scene.from_dict(data))

        self.logger.info(f"Scene plan loaded: {len(scenes)} scenes from {work_id}")

        return scenes

    def export_csv(self, work_id: str, scenes: List[Scene], output_path: Optional[Path] = None) -> Path:
        """Export scene plan to CSV.

        Args:
            work_id: Work identifier
            scenes: List of scenes
            output_path: Optional custom output path

        Returns:
            Path to CSV file

        Privacy Note:
            CSV contains block IDs only, not content.
        """
        if output_path is None:
            output_path = self.scenes_dir / f"{work_id}_scenes.csv"

        with output_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(Scene.csv_headers())
            for scene in scenes:
                writer.writerow(scene.to_csv_row())

        self.logger.info(f"Scene plan exported to CSV: {output_path.name}")

        return output_path

    def expand_template(
        self,
        work_id: str,
        base_blocks: Dict[str, str],
        variations: List[Dict[str, Any]]
    ) -> List[Scene]:
        """Expand scene template with variations.

        Args:
            work_id: Work identifier
            base_blocks: Base block IDs shared across scenes
            variations: List of variation configs

        Returns:
            List of Scene instances

        Example:
            base_blocks = {
                "quality_id": "quality_001",
                "character_id": "char_001",
                "private_id": "private_001",
                "negative_id": "negative_001"
            }
            variations = [
                {
                    "setting_id": "beach",
                    "lighting_id": "sunset",
                    "camera_id": ["wide", "closeup", "aerial"]
                }
            ]
        """
        scenes = []
        scene_no = 1

        for variation in variations:
            camera_ids = variation.get("camera_id", [])
            if isinstance(camera_ids, str):
                camera_ids = [camera_ids]

            for camera_id in camera_ids:
                scene_config = {
                    "scene_no": scene_no,
                    **base_blocks,
                    "setting_id": variation["setting_id"],
                    "lighting_id": variation["lighting_id"],
                    "camera_id": camera_id
                }

                scenes.append(self._create_scene(work_id, scene_config))
                scene_no += 1

        return scenes
