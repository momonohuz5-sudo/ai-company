"""ComfyUI workflow template management."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from .models import Scene, PromptBlock
from .storage import Storage
from .logger import PrivacySafeLogger


class WorkflowManager:
    """Manages ComfyUI workflow templates and prompt injection."""

    def __init__(self, workflows_dir: Path, logger: PrivacySafeLogger):
        """Initialize workflow manager.

        Args:
            workflows_dir: Directory containing workflow templates
            logger: Logger instance
        """
        self.workflows_dir = workflows_dir
        self.logger = logger
        Storage.ensure_dir(workflows_dir)

    def load_template(self, template_name: str = "default") -> Dict[str, Any]:
        """Load workflow template.

        Args:
            template_name: Template name (without .json extension)

        Returns:
            Workflow template dict

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_file = self.workflows_dir / f"{template_name}.json"

        if not template_file.exists():
            raise FileNotFoundError(f"Workflow template not found: {template_name}")

        return Storage.load_json(template_file)

    def build_workflow(
        self,
        scene: Scene,
        blocks: Dict[str, PromptBlock],
        private_blocks: Dict[str, Dict[str, Any]],
        template_name: str = "default"
    ) -> Dict[str, Any]:
        """Build ComfyUI workflow from scene and blocks.

        Args:
            scene: Scene to build workflow for
            blocks: General prompt blocks dict (type -> block)
            private_blocks: Private block content (loaded externally)
            template_name: Workflow template to use

        Returns:
            Complete ComfyUI workflow dict

        Privacy Note:
            This method receives private_blocks from external source.
            The pipeline tool itself never reads private block files.
        """
        workflow = self.load_template(template_name)

        quality_block = blocks.get("quality")
        character_block = blocks.get("character")
        setting_block = blocks.get("setting")
        lighting_block = blocks.get("lighting")
        camera_block = blocks.get("camera")

        positive_parts = []
        if quality_block:
            positive_parts.append(quality_block.content)
        if character_block:
            positive_parts.append(character_block.content)
        if setting_block:
            positive_parts.append(setting_block.content)
        if lighting_block:
            positive_parts.append(lighting_block.content)
        if camera_block:
            positive_parts.append(camera_block.content)

        private_content = private_blocks.get("private", {}).get("content", "")
        if private_content:
            positive_parts.append(private_content)

        positive_prompt = ", ".join(positive_parts)
        negative_prompt = private_blocks.get("negative", {}).get("content", "")

        workflow = self._inject_prompts(
            workflow,
            positive_prompt,
            negative_prompt,
            scene.seed,
            quality_block.parameters if quality_block else {}
        )

        self.logger.debug(f"Workflow built for scene {scene.scene_no:03d}")

        return workflow

    def _inject_prompts(
        self,
        workflow: Dict[str, Any],
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inject prompts and parameters into workflow.

        Args:
            workflow: Base workflow template
            positive_prompt: Positive prompt text
            negative_prompt: Negative prompt text
            seed: Random seed
            parameters: Generation parameters

        Returns:
            Modified workflow
        """
        workflow = json.loads(json.dumps(workflow))

        for node_id, node in workflow.items():
            class_type = node.get("class_type", "")

            if class_type == "CLIPTextEncode":
                inputs = node.get("inputs", {})
                if "text" in inputs:
                    if "positive" in str(node_id).lower() or inputs.get("text") == "{{positive_prompt}}":
                        inputs["text"] = positive_prompt
                    elif "negative" in str(node_id).lower() or inputs.get("text") == "{{negative_prompt}}":
                        inputs["text"] = negative_prompt

            elif class_type == "KSampler":
                inputs = node.get("inputs", {})
                inputs["seed"] = seed
                if "steps" in parameters:
                    inputs["steps"] = parameters["steps"]
                if "cfg_scale" in parameters:
                    inputs["cfg"] = parameters["cfg_scale"]
                if "sampler" in parameters:
                    inputs["sampler_name"] = parameters["sampler"]

            elif class_type == "EmptyLatentImage":
                inputs = node.get("inputs", {})
                if "width" in parameters:
                    inputs["width"] = parameters["width"]
                if "height" in parameters:
                    inputs["height"] = parameters["height"]

        return workflow

    def save_workflow(self, workflow: Dict[str, Any], output_path: Path) -> None:
        """Save workflow to file.

        Args:
            workflow: Workflow dict
            output_path: Output file path
        """
        Storage.save_json(output_path, workflow)
        self.logger.info(f"Workflow saved: {output_path.name}")
