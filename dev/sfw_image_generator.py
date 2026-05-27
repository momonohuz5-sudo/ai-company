#!/usr/bin/env python3
"""
SFW Image Generator CLI
AI Company - Development Department

Main CLI tool for SFW image generation using ComfyUI Cloud
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List

from comfyui_integration import ComfyUIClient, WorkflowManager, create_default_workflows
from prompt_manager import PromptManager, PromptCategory
from image_organizer import ImageOrganizer, BatchProcessor, GenerationStatus


class SFWImageGenerator:
    """Main CLI application for SFW image generation"""

    def __init__(self):
        self.client = ComfyUIClient()
        self.workflow_manager = WorkflowManager()
        self.prompt_manager = PromptManager()
        self.organizer = ImageOrganizer()
        self.batch_processor = BatchProcessor(self.organizer)

    def generate(
        self,
        prompt: str,
        template: Optional[str] = None,
        workflow: Optional[str] = None,
        category: str = 'general',
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Generate a single image"""
        if template:
            final_prompt = self.prompt_manager.generate_prompt(template, **kwargs)
            if not final_prompt:
                return f"Error: Template '{template}' not found"
        else:
            final_prompt = prompt

        print(f"Generating image with prompt: {final_prompt}")

        workflow_config = None
        if workflow:
            workflow_config = self.workflow_manager.load_workflow(workflow)
            if workflow_config:
                kwargs.update(workflow_config['default_params'])

        job_id = f"gen_{int(__import__('time').time())}"

        metadata = self.organizer.create_job(
            job_id=job_id,
            prompt=final_prompt,
            negative_prompt=kwargs.get('negative_prompt', ''),
            parameters=kwargs,
            category=category,
            tags=tags or []
        )

        self.organizer.update_status(job_id, GenerationStatus.PROCESSING)

        result = self.client.generate_image(
            prompt=final_prompt,
            negative_prompt=kwargs.get('negative_prompt', ''),
            width=kwargs.get('width', 1024),
            height=kwargs.get('height', 1024),
            steps=kwargs.get('steps', 30),
            cfg_scale=kwargs.get('cfg_scale', 7.0),
            seed=kwargs.get('seed'),
            workflow_id=kwargs.get('workflow_id')
        )

        if result.get('success') and result.get('image_url'):
            save_path = f"./temp_{job_id}.png"
            if self.client.download_result(result['image_url'], save_path):
                final_path = self.organizer.save_image(job_id, save_path)
                Path(save_path).unlink(missing_ok=True)

                self.prompt_manager.save_to_history(
                    prompt=final_prompt,
                    template_name=template,
                    parameters=kwargs,
                    result=result
                )

                return f"✓ Image saved to: {final_path}\n  Job ID: {job_id}"
            else:
                self.organizer.update_status(job_id, GenerationStatus.FAILED, "Download failed")
                return f"Error: Failed to download image"
        else:
            error = result.get('error', 'Unknown error')
            self.organizer.update_status(job_id, GenerationStatus.FAILED, error)
            return f"Error: {error}"

    def batch_generate(
        self,
        prompts: List[str],
        category: str = 'batch',
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Generate multiple images"""
        print(f"Creating batch with {len(prompts)} prompts...")

        job_ids = self.batch_processor.create_batch(
            prompts=prompts,
            base_params=kwargs,
            category=category,
            tags=tags
        )

        print(f"Created {len(job_ids)} jobs")
        print("Starting generation...")

        for job_id, prompt in zip(job_ids, prompts):
            self.organizer.update_status(job_id, GenerationStatus.PROCESSING)

            result = self.client.generate_image(
                prompt=prompt,
                negative_prompt=kwargs.get('negative_prompt', ''),
                width=kwargs.get('width', 1024),
                height=kwargs.get('height', 1024),
                steps=kwargs.get('steps', 30),
                cfg_scale=kwargs.get('cfg_scale', 7.0)
            )

            if result.get('success') and result.get('image_url'):
                save_path = f"./temp_{job_id}.png"
                if self.client.download_result(result['image_url'], save_path):
                    self.organizer.save_image(job_id, save_path)
                    Path(save_path).unlink(missing_ok=True)
                    print(f"  ✓ {job_id}")
                else:
                    self.organizer.update_status(job_id, GenerationStatus.FAILED, "Download failed")
                    print(f"  ✗ {job_id} - Download failed")
            else:
                self.organizer.update_status(job_id, GenerationStatus.FAILED, result.get('error'))
                print(f"  ✗ {job_id} - {result.get('error')}")

        status = self.batch_processor.get_batch_status('batch')
        return f"\nBatch complete:\n{json.dumps(status, indent=2)}"

    def list_templates(self, category: Optional[str] = None) -> str:
        """List available prompt templates"""
        cat_enum = PromptCategory(category) if category else None
        templates = self.prompt_manager.list_templates(cat_enum)

        output = [f"Available templates ({len(templates)}):"]
        for tmpl in templates:
            output.append(f"  • {tmpl.name} ({tmpl.category.value})")
            output.append(f"    Variables: {', '.join(tmpl.variables)}")
            output.append(f"    Tags: {', '.join(tmpl.tags)}")

        return '\n'.join(output)

    def list_workflows(self) -> str:
        """List available workflows"""
        workflows = self.workflow_manager.list_workflows()

        output = [f"Available workflows ({len(workflows)}):"]
        for wf in workflows:
            config = self.workflow_manager.load_workflow(wf)
            output.append(f"  • {wf}")
            output.append(f"    {config['description']}")

        return '\n'.join(output)

    def show_stats(self) -> str:
        """Show generation statistics"""
        stats = self.organizer.get_statistics()

        output = ["Generation Statistics:"]
        output.append(f"  Total jobs: {stats['total_jobs']}")
        output.append(f"  Completed: {stats['completed_count']}")
        output.append(f"  Total size: {stats['total_size_mb']} MB")
        output.append("\n  By status:")
        for status, count in stats['by_status'].items():
            output.append(f"    {status}: {count}")
        output.append("\n  By category:")
        for category, count in stats['by_category'].items():
            output.append(f"    {category}: {count}")

        return '\n'.join(output)

    def list_images(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """List generated images"""
        status_enum = GenerationStatus(status) if status else None
        images = self.organizer.list_images(
            category=category,
            status=status_enum,
            limit=limit
        )

        output = [f"Generated images ({len(images)}):"]
        for img in images:
            output.append(f"\n  Job ID: {img.id}")
            output.append(f"  Status: {img.status.value}")
            output.append(f"  Category: {img.category}")
            output.append(f"  Prompt: {img.prompt[:60]}...")
            output.append(f"  Size: {img.width}x{img.height}")
            output.append(f"  Created: {img.created_at}")

        return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='SFW Image Generator - ComfyUI Cloud Integration'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    gen_parser = subparsers.add_parser('generate', help='Generate single image')
    gen_parser.add_argument('prompt', help='Generation prompt')
    gen_parser.add_argument('--template', '-t', help='Use prompt template')
    gen_parser.add_argument('--workflow', '-w', help='Use workflow preset')
    gen_parser.add_argument('--category', '-c', default='general', help='Image category')
    gen_parser.add_argument('--tags', nargs='+', help='Image tags')
    gen_parser.add_argument('--width', type=int, default=1024)
    gen_parser.add_argument('--height', type=int, default=1024)
    gen_parser.add_argument('--steps', type=int, default=30)
    gen_parser.add_argument('--cfg-scale', type=float, default=7.0)
    gen_parser.add_argument('--seed', type=int)

    batch_parser = subparsers.add_parser('batch', help='Generate multiple images')
    batch_parser.add_argument('prompts_file', help='JSON file with prompts array')
    batch_parser.add_argument('--category', '-c', default='batch')
    batch_parser.add_argument('--tags', nargs='+')

    subparsers.add_parser('templates', help='List prompt templates')
    subparsers.add_parser('workflows', help='List workflows')
    subparsers.add_parser('stats', help='Show statistics')

    list_parser = subparsers.add_parser('list', help='List generated images')
    list_parser.add_argument('--category', '-c')
    list_parser.add_argument('--status', '-s')
    list_parser.add_argument('--limit', '-l', type=int, default=10)

    subparsers.add_parser('init', help='Initialize default templates and workflows')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    gen = SFWImageGenerator()

    if args.command == 'generate':
        kwargs = {
            'width': args.width,
            'height': args.height,
            'steps': args.steps,
            'cfg_scale': args.cfg_scale,
        }
        if args.seed:
            kwargs['seed'] = args.seed

        result = gen.generate(
            prompt=args.prompt,
            template=args.template,
            workflow=args.workflow,
            category=args.category,
            tags=args.tags,
            **kwargs
        )
        print(result)

    elif args.command == 'batch':
        with open(args.prompts_file, 'r') as f:
            prompts = json.load(f)

        result = gen.batch_generate(
            prompts=prompts,
            category=args.category,
            tags=args.tags
        )
        print(result)

    elif args.command == 'templates':
        print(gen.list_templates())

    elif args.command == 'workflows':
        print(gen.list_workflows())

    elif args.command == 'stats':
        print(gen.show_stats())

    elif args.command == 'list':
        print(gen.list_images(
            category=args.category,
            status=args.status,
            limit=args.limit
        ))

    elif args.command == 'init':
        print("Initializing default templates and workflows...")
        create_default_workflows()
        print("✓ Workflows created")
        print("✓ Templates created")
        print("\nRun 'python sfw_image_generator.py templates' to see available templates")
        print("Run 'python sfw_image_generator.py workflows' to see available workflows")


if __name__ == '__main__':
    main()
