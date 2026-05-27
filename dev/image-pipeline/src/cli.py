"""Command-line interface for the image production pipeline."""

import click
import sys
import json
from pathlib import Path
from typing import Optional

from .config import load_config
from .logger import get_logger
from .project_manager import ProjectManager
from .prompt_manager import PromptManager
from .scene_planner import ScenePlanner
from .comfyui_client import ComfyUIClient
from .organizer import Organizer
from .approval import ApprovalManager
from .packager import Packager
from .metadata import MetadataExporter
from .compliance import ComplianceChecker


def get_pipeline_root() -> Path:
    """Get pipeline root directory."""
    return Path(__file__).parent.parent


@click.group()
@click.option('--config', type=click.Path(exists=True, path_type=Path), help='Config file path')
@click.pass_context
def cli(ctx, config):
    """ComfyUI Image Production Pipeline CLI."""
    root_dir = get_pipeline_root()

    if config is None:
        config = root_dir / "config" / "settings.yaml"
        if not config.exists():
            config = None

    ctx.obj = {
        'config': load_config(config, root_dir),
        'root_dir': root_dir
    }


@cli.group()
def work():
    """Work/project management commands."""
    pass


@work.command('create')
@click.argument('work_id')
@click.option('--title', required=True, help='Work title')
@click.option('--description', default='', help='Work description')
@click.pass_context
def work_create(ctx, work_id, title, description):
    """Create a new work."""
    config = ctx.obj['config']
    logger = get_logger('work', config.logs_dir)

    pm = ProjectManager(config.get_work_dir(work_id).parent, logger)

    try:
        work_obj = pm.create_work(work_id, title, description)
        click.echo(f"✓ Work created: {work_id}")
        click.echo(f"  Title: {title}")
        click.echo(f"  Status: {work_obj.status}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@work.command('list')
@click.pass_context
def work_list(ctx):
    """List all works."""
    config = ctx.obj['config']
    logger = get_logger('work', config.logs_dir)

    pm = ProjectManager(config.get_work_dir('').parent, logger)

    works = pm.list_works()

    if not works:
        click.echo("No works found.")
        return

    click.echo(f"\nTotal works: {len(works)}\n")

    for w in works:
        click.echo(f"  {w.work_id}")
        click.echo(f"    Title: {w.title}")
        click.echo(f"    Status: {w.status}")
        click.echo(f"    Created: {w.created_at}")
        click.echo()


@work.command('show')
@click.argument('work_id')
@click.pass_context
def work_show(ctx, work_id):
    """Show work details."""
    config = ctx.obj['config']
    logger = get_logger('work', config.logs_dir)

    pm = ProjectManager(config.get_work_dir(work_id).parent, logger)

    try:
        w = pm.get_work(work_id)
        click.echo(f"\nWork: {w.work_id}")
        click.echo(f"  Title: {w.title}")
        click.echo(f"  Description: {w.description or '(none)'}")
        click.echo(f"  Status: {w.status}")
        click.echo(f"  Created: {w.created_at}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def block():
    """Prompt block management commands."""
    pass


@block.command('create')
@click.option('--type', 'block_type', required=True,
              type=click.Choice(['quality', 'character', 'setting', 'lighting', 'camera']))
@click.option('--content', required=True, help='Block content (prompt text)')
@click.option('--parameters', help='Parameters JSON (for quality blocks)')
@click.option('--tags', help='Comma-separated tags')
@click.option('--id', 'block_id', help='Custom block ID')
@click.pass_context
def block_create(ctx, block_type, content, parameters, tags, block_id):
    """Create a general prompt block."""
    config = ctx.obj['config']
    logger = get_logger('block', config.logs_dir)

    pm = PromptManager(config.data_dir / "blocks", config.private_dir, logger)

    params = {}
    if parameters:
        try:
            params = json.loads(parameters)
        except json.JSONDecodeError:
            click.echo("✗ Invalid parameters JSON", err=True)
            sys.exit(1)

    tag_list = [t.strip() for t in tags.split(',')] if tags else []

    try:
        block_obj = pm.create_block(block_type, content, params, tag_list, block_id)
        click.echo(f"✓ Block created: {block_obj.block_id}")
        click.echo(f"  Type: {block_type}")
        click.echo(f"  Tags: {', '.join(tag_list) if tag_list else '(none)'}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@block.command('create-private-ref')
@click.option('--type', 'block_type', required=True,
              type=click.Choice(['private', 'negative']))
@click.option('--id', 'block_id', help='Custom block ID')
@click.pass_context
def block_create_private_ref(ctx, block_type, block_id):
    """Create OPAQUE reference to private/negative block."""
    config = ctx.obj['config']
    logger = get_logger('block', config.logs_dir)

    pm = PromptManager(config.data_dir / "blocks", config.private_dir, logger)

    try:
        ref = pm.create_private_ref(block_type, block_id)
        click.echo(f"✓ Private block reference created: {ref.block_id}")
        click.echo(f"  Type: {block_type}")
        click.echo()
        click.echo("IMPORTANT: You must manually create the JSON file:")
        click.echo(f"  {config.private_dir / 'blocks' / f'{ref.block_id}.json'}")
        click.echo()
        click.echo("This tool will NEVER access the content of private blocks.")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@block.command('list')
@click.option('--type', 'block_type', required=True,
              type=click.Choice(['quality', 'character', 'setting', 'lighting', 'camera']))
@click.pass_context
def block_list(ctx, block_type):
    """List blocks by type."""
    config = ctx.obj['config']
    logger = get_logger('block', config.logs_dir)

    pm = PromptManager(config.data_dir / "blocks", config.private_dir, logger)

    blocks = pm.list_blocks(block_type)

    if not blocks:
        click.echo(f"No {block_type} blocks found.")
        return

    click.echo(f"\n{block_type.capitalize()} blocks: {len(blocks)}\n")

    for b in blocks:
        click.echo(f"  {b.block_id}")
        click.echo(f"    Content: {b.content[:60]}..." if len(b.content) > 60 else f"    Content: {b.content}")
        if b.parameters:
            click.echo(f"    Parameters: {b.parameters}")
        if b.tags:
            click.echo(f"    Tags: {', '.join(b.tags)}")
        click.echo()


@cli.group()
def scene():
    """Scene planning commands."""
    pass


@scene.command('plan')
@click.argument('work_id')
@click.option('--config-file', type=click.Path(exists=True, path_type=Path),
              required=True, help='Scene configuration JSON file')
@click.pass_context
def scene_plan(ctx, work_id, config_file):
    """Create scene plan from configuration file."""
    config = ctx.obj['config']
    logger = get_logger('scene', config.logs_dir)

    pm_proj = ProjectManager(config.get_work_dir(work_id).parent, logger)
    pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
    sp = ScenePlanner(
        config.get_scenes_dir(),
        config.output_dir,
        pm_prompt,
        logger,
        config.default_seed_start,
        config.seed_increment
    )

    if not pm_proj.work_exists(work_id):
        click.echo(f"✗ Work not found: {work_id}", err=True)
        sys.exit(1)

    try:
        with config_file.open('r') as f:
            scenes_config = json.load(f)

        scenes = sp.create_scene_plan(work_id, scenes_config)
        plan_file = sp.save_plan(work_id, scenes)

        click.echo(f"✓ Scene plan created: {len(scenes)} scenes")
        click.echo(f"  Saved to: {plan_file}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@scene.command('export')
@click.argument('work_id')
@click.option('--format', type=click.Choice(['csv', 'jsonl']), default='csv')
@click.pass_context
def scene_export(ctx, work_id, format):
    """Export scene plan to CSV or JSONL."""
    config = ctx.obj['config']
    logger = get_logger('scene', config.logs_dir)

    pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
    sp = ScenePlanner(
        config.get_scenes_dir(),
        config.output_dir,
        pm_prompt,
        logger
    )

    try:
        scenes = sp.load_plan(work_id)

        if format == 'csv':
            output_file = sp.export_csv(work_id, scenes)
        else:
            output_file = config.get_scenes_dir() / f"{work_id}_scenes.jsonl"

        click.echo(f"✓ Scene plan exported to {format.upper()}: {output_file}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def generate():
    """ComfyUI generation commands."""
    pass


@generate.command('submit')
@click.argument('work_id')
@click.option('--dry-run', is_flag=True, help='Dry-run mode (override config)')
@click.pass_context
def generate_submit(ctx, work_id, dry_run):
    """Submit batch to ComfyUI."""
    config = ctx.obj['config']
    logger = get_logger('generate', config.logs_dir)

    pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
    sp = ScenePlanner(
        config.get_scenes_dir(),
        config.output_dir,
        pm_prompt,
        logger
    )

    dry_run_mode = dry_run or config.dry_run

    client = ComfyUIClient(
        config.comfyui_endpoint,
        config.comfyui_timeout,
        dry_run_mode,
        logger
    )

    try:
        scenes = sp.load_plan(work_id)

        if dry_run_mode:
            click.echo("DRY-RUN MODE: No actual API calls will be made\n")

        job_ids = client.submit_batch(scenes)

        click.echo(f"✓ Batch submitted: {len(job_ids)} scenes")

        if not dry_run_mode:
            success = sum(1 for jid in job_ids if jid is not None)
            click.echo(f"  Success: {success}/{len(job_ids)}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command('approve')
@click.argument('work_id')
@click.argument('image_path', type=click.Path(exists=True, path_type=Path))
@click.pass_context
def approve(ctx, work_id, image_path):
    """Mark an image as approved."""
    config = ctx.obj['config']
    logger = get_logger('approval', config.logs_dir)

    am = ApprovalManager(config.output_dir, logger)

    try:
        approved_path = am.mark_approved(work_id, image_path)
        click.echo(f"✓ Image approved: {image_path.name}")
        click.echo(f"  Saved to: {approved_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command('package')
@click.argument('work_id')
@click.pass_context
def package(ctx, work_id):
    """Package approved images for distribution."""
    config = ctx.obj['config']
    logger = get_logger('package', config.logs_dir)

    pm_proj = ProjectManager(config.get_work_dir(work_id).parent, logger)
    pm_prompt = PromptManager(config.data_dir / "blocks", config.private_dir, logger)
    sp = ScenePlanner(config.get_scenes_dir(), config.output_dir, pm_prompt, logger)
    am = ApprovalManager(config.output_dir, logger)
    packager = Packager(config.output_dir, logger)
    metadata_exp = MetadataExporter(logger)

    try:
        work_obj = pm_proj.get_work(work_id)
        scenes = sp.load_plan(work_id)

        renumbered = packager.renumber_images(work_id, config.renumber_start)
        click.echo(f"✓ Renumbered {len(renumbered)} images")

        if config.sample_count > 0:
            samples, sales = packager.separate_samples(work_id, config.sample_count)
            click.echo(f"✓ Separated {len(samples)} samples and {len(sales)} sales images")

        metadata_path = config.get_output_work_dir(work_id) / "package" / "metadata.json"
        approved_count = len(am.list_approved(work_id))
        metadata_exp.export_metadata(work_obj, scenes, approved_count, metadata_path)
        click.echo(f"✓ Metadata exported")

        if config.get("packaging", "create_zip", default=True):
            zip_path = packager.create_package(work_id)
            click.echo(f"✓ Package created: {zip_path}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command('compliance')
@click.argument('work_id')
@click.pass_context
def compliance(ctx, work_id):
    """Generate compliance checklist."""
    config = ctx.obj['config']
    logger = get_logger('compliance', config.logs_dir)

    pm = ProjectManager(config.get_work_dir(work_id).parent, logger)
    checker = ComplianceChecker(logger)

    try:
        work_obj = pm.get_work(work_id)
        checklist_path = config.get_output_work_dir(work_id) / "compliance_checklist.md"
        checker.generate_checklist(work_obj, checklist_path)

        click.echo(f"✓ Compliance checklist generated: {checklist_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
