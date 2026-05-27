"""
ComfyUI Cloud API Integration for SFW Image Generation
AI Company - Development Department
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class ComfyUIClient:
    """ComfyUI Cloud API client for SFW image generation"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('COMFYUI_API_KEY')
        self.base_url = base_url or os.getenv('COMFYUI_BASE_URL', 'https://api.comfy.cloud/v1')
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: Optional[int] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SFW image using ComfyUI

        Args:
            prompt: Main generation prompt (SFW content only)
            negative_prompt: Things to avoid in generation
            width: Image width in pixels
            height: Image height in pixels
            steps: Number of generation steps
            cfg_scale: CFG scale for prompt adherence
            seed: Random seed (None for random)
            workflow_id: Custom workflow ID if using pre-configured workflow

        Returns:
            Response dictionary with generation results
        """
        payload = {
            'prompt': self._ensure_sfw_prompt(prompt),
            'negative_prompt': self._get_nsfw_negative_prompt() + ', ' + negative_prompt,
            'width': width,
            'height': height,
            'steps': steps,
            'cfg_scale': cfg_scale,
        }

        if seed is not None:
            payload['seed'] = seed

        if workflow_id:
            payload['workflow_id'] = workflow_id

        try:
            response = self.session.post(f'{self.base_url}/generate', json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e), 'success': False}

    def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check generation job status"""
        try:
            response = self.session.get(f'{self.base_url}/jobs/{job_id}')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e), 'success': False}

    def download_result(self, result_url: str, save_path: str) -> bool:
        """Download generated image"""
        try:
            response = self.session.get(result_url, stream=True)
            response.raise_for_status()

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def _ensure_sfw_prompt(self, prompt: str) -> str:
        """Ensure prompt is SFW by adding safety tags"""
        sfw_keywords = ['safe for work', 'family friendly', 'professional']
        return prompt + ', ' + ', '.join(sfw_keywords)

    def _get_nsfw_negative_prompt(self) -> str:
        """Get comprehensive NSFW negative prompt"""
        return (
            'nsfw, nude, nudity, explicit, adult content, sexual, '
            'provocative, inappropriate, mature content, 18+, r18'
        )


class WorkflowManager:
    """Manage ComfyUI workflows for different use cases"""

    def __init__(self, workflows_dir: str = './workflows'):
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def create_workflow(
        self,
        name: str,
        description: str,
        default_params: Dict[str, Any]
    ) -> str:
        """Create a new workflow configuration"""
        workflow = {
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'default_params': default_params,
            'category': 'sfw'
        }

        workflow_path = self.workflows_dir / f"{name}.json"
        with open(workflow_path, 'w') as f:
            json.dump(workflow, f, indent=2)

        return str(workflow_path)

    def load_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """Load workflow configuration"""
        workflow_path = self.workflows_dir / f"{name}.json"
        if not workflow_path.exists():
            return None

        with open(workflow_path, 'r') as f:
            return json.load(f)

    def list_workflows(self) -> List[str]:
        """List all available workflows"""
        return [f.stem for f in self.workflows_dir.glob('*.json')]


def create_default_workflows():
    """Create default SFW workflow templates"""
    manager = WorkflowManager()

    workflows = [
        {
            'name': 'landscape',
            'description': 'Natural landscape and scenery generation',
            'default_params': {
                'negative_prompt': 'people, buildings, text',
                'width': 1920,
                'height': 1080,
                'steps': 40,
                'cfg_scale': 7.0
            }
        },
        {
            'name': 'product_design',
            'description': 'Product mockups and design visualization',
            'default_params': {
                'negative_prompt': 'messy, cluttered, low quality',
                'width': 1024,
                'height': 1024,
                'steps': 30,
                'cfg_scale': 8.0
            }
        },
        {
            'name': 'illustration',
            'description': 'Artistic illustrations and concept art',
            'default_params': {
                'negative_prompt': 'photorealistic, blurry, low quality',
                'width': 1024,
                'height': 1536,
                'steps': 35,
                'cfg_scale': 7.5
            }
        },
        {
            'name': 'ui_mockup',
            'description': 'UI/UX design mockups',
            'default_params': {
                'negative_prompt': 'messy, unprofessional, cluttered',
                'width': 1440,
                'height': 900,
                'steps': 25,
                'cfg_scale': 7.0
            }
        },
        {
            'name': 'marketing_visual',
            'description': 'Marketing and promotional visuals',
            'default_params': {
                'negative_prompt': 'low quality, amateur, ugly',
                'width': 1200,
                'height': 630,
                'steps': 30,
                'cfg_scale': 7.5
            }
        }
    ]

    created = []
    for wf in workflows:
        path = manager.create_workflow(
            wf['name'],
            wf['description'],
            wf['default_params']
        )
        created.append(path)

    return created


if __name__ == '__main__':
    print("ComfyUI Integration Module")
    print("Creating default SFW workflows...")
    paths = create_default_workflows()
    print(f"Created {len(paths)} default workflows")
    for p in paths:
        print(f"  - {p}")
