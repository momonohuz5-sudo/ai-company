"""Demo script for end-to-end image generation workflow."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.logger import get_logger
from src.project_manager import ProjectManager
from src.prompt_manager import PromptManager
from src.scene_planner import ScenePlanner
from src.workflow_manager import WorkflowManager
from src.comfyui_client import ComfyUIClient
from src.storage import Storage


def main():
    """Run demo workflow."""
    print("=" * 60)
    print("ComfyUI Image Production Pipeline - Demo Workflow")
    print("=" * 60)
    print()

    # Load config
    root_dir = Path(__file__).parent.parent
    config_path = root_dir / "config" / "settings.yaml"

    if not config_path.exists():
        config_path = None

    config = load_config(config_path, root_dir)
    logger = get_logger("demo", config.logs_dir)

    print("✓ Configuration loaded")
    print(f"  ComfyUI endpoint: {config.comfyui_endpoint}")
    print(f"  Dry-run mode: {config.dry_run}")
    print()

    # Initialize managers
    pm_proj = ProjectManager(config.get_work_dir("").parent, logger)
    pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
    sp = ScenePlanner(
        config.get_scenes_dir(),
        config.output_dir,
        pm_prompt,
        logger,
        config.default_seed_start,
        config.seed_increment
    )
    wm = WorkflowManager(root_dir / "workflows", logger)
    comfy = ComfyUIClient(
        config.comfyui_endpoint,
        config.comfyui_timeout,
        config.dry_run,
        logger
    )

    print("✓ Managers initialized")
    print()

    # Check ComfyUI connection
    print("Checking ComfyUI connection...")
    if comfy.check_connection():
        print("✓ ComfyUI connection OK")
    else:
        print("✗ ComfyUI not reachable (continuing in dry-run mode)")
    print()

    # Step 1: Create work
    work_id = "demo_work_001"
    print(f"Step 1: Creating work '{work_id}'...")

    if pm_proj.work_exists(work_id):
        print(f"  Work already exists, skipping creation")
        work = pm_proj.get_work(work_id)
    else:
        work = pm_proj.create_work(
            work_id,
            "Demo Work - Sunset Beach",
            "Demonstration of the image production pipeline"
        )
        print(f"✓ Work created: {work.title}")
    print()

    # Step 2: Create prompt blocks
    print("Step 2: Creating prompt blocks...")

    blocks_to_create = [
        {
            "type": "quality",
            "id": "quality_hd",
            "content": "masterpiece, best quality, ultra detailed, 8k uhd",
            "parameters": {
                "steps": 25,
                "cfg_scale": 7.5,
                "sampler": "euler",
                "width": 768,
                "height": 1024
            }
        },
        {
            "type": "character",
            "id": "char_woman_beach",
            "content": "1girl, young woman, long flowing hair, white sundress, barefoot, relaxed pose"
        },
        {
            "type": "setting",
            "id": "setting_beach",
            "content": "tropical beach, white sand, turquoise ocean, palm trees, clear sky"
        },
        {
            "type": "lighting",
            "id": "lighting_sunset",
            "content": "golden hour, warm sunset lighting, soft shadows, atmospheric glow, rim light"
        },
        {
            "type": "camera",
            "id": "camera_wide",
            "content": "wide shot, full body visible, dynamic angle, depth of field"
        }
    ]

    created_blocks = {}
    for block_config in blocks_to_create:
        block_type = block_config["type"]
        block_id = block_config["id"]

        try:
            block = pm_prompt.get_block(block_id, block_type)
            print(f"  {block_type}/{block_id} already exists")
        except FileNotFoundError:
            block = pm_prompt.create_block(
                block_type,
                block_config["content"],
                block_config.get("parameters", {}),
                block_id=block_id
            )
            print(f"✓ Created {block_type}/{block_id}")

        created_blocks[block_type] = block

    print()

    # Step 3: Create private block references
    print("Step 3: Creating private block references...")

    private_ref_id = "private_demo_001"
    negative_ref_id = "negative_demo_001"

    for block_type, block_id in [("private", private_ref_id), ("negative", negative_ref_id)]:
        marker_file = config.private_dir / "blocks" / f"{block_id}.marker"
        json_file = config.private_dir / "blocks" / f"{block_id}.json"

        if not marker_file.exists():
            pm_prompt.create_private_ref(block_type, block_id)

            # Create placeholder private content
            if not json_file.exists():
                private_content = {
                    "content": "(User should edit this with actual private content)" if block_type == "private" else "lowres, bad anatomy, bad hands, text, error, missing fingers",
                    "tags": []
                }
                Storage.save_json(json_file, private_content)
                print(f"✓ Created {block_type} reference and placeholder: {block_id}")
        else:
            print(f"  {block_type}/{block_id} already exists")

    print()

    # Step 4: Create scene plan
    print("Step 4: Creating scene plan...")

    scenes_config = []
    for i in range(1, 4):  # 3 scenes
        scenes_config.append({
            "scene_no": i,
            "quality_id": "quality_hd",
            "character_id": "char_woman_beach",
            "setting_id": "setting_beach",
            "lighting_id": "lighting_sunset",
            "camera_id": "camera_wide",
            "private_id": private_ref_id,
            "negative_id": negative_ref_id,
            "seed": 1000 + i
        })

    scenes = sp.create_scene_plan(work_id, scenes_config, validate_blocks=True)
    plan_file = sp.save_plan(work_id, scenes)

    print(f"✓ Scene plan created: {len(scenes)} scenes")
    print(f"  Saved to: {plan_file.name}")
    print()

    # Step 5: Build workflows
    print("Step 5: Building ComfyUI workflows...")

    workflows = []
    for scene in scenes:
        # Load private blocks
        private_file = config.private_dir / "blocks" / f"{scene.private_id}.json"
        negative_file = config.private_dir / "blocks" / f"{scene.negative_id}.json"

        private_blocks = {
            "private": Storage.load_json(private_file) if private_file.exists() else {},
            "negative": Storage.load_json(negative_file) if negative_file.exists() else {}
        }

        # Build workflow
        workflow = wm.build_workflow(scene, created_blocks, private_blocks)
        workflows.append(workflow)

        print(f"✓ Workflow built for scene {scene.scene_no:03d}")

    print()

    # Step 6: Submit to ComfyUI
    print("Step 6: Submitting to ComfyUI...")

    if config.dry_run:
        print("  (Running in DRY-RUN mode - no actual API calls)")
        print()

    job_ids = comfy.submit_batch_with_workflows(scenes, workflows)

    print()
    print(f"✓ Batch submission completed")
    print(f"  Total scenes: {len(scenes)}")
    print(f"  Successful: {sum(1 for jid in job_ids if jid)}")
    print()

    if job_ids and job_ids[0]:
        print("Job IDs:")
        for i, jid in enumerate(job_ids, 1):
            if jid:
                print(f"  Scene {i}: {jid}")
    print()

    # Summary
    print("=" * 60)
    print("Demo workflow completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    if config.dry_run:
        print("1. Set 'dry_run: false' in config/settings.yaml")
        print("2. Ensure ComfyUI is running")
        print("3. Edit private blocks with actual content:")
        print(f"   - {config.private_dir / 'blocks' / f'{private_ref_id}.json'}")
        print(f"   - {config.private_dir / 'blocks' / f'{negative_ref_id}.json'}")
        print("4. Re-run this demo to generate actual images")
    else:
        print("1. Wait for ComfyUI to complete generation")
        print("2. Approve generated images:")
        print(f"   python -m src.cli approve {work_id} <image_path>")
        print("3. Package approved images:")
        print(f"   python -m src.cli package {work_id}")
    print()


if __name__ == "__main__":
    main()
