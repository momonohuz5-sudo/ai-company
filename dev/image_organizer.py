"""
Image Generation Organization and Management System
AI Company - Development Department
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class GenerationStatus(Enum):
    """Status of image generation job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ImageMetadata:
    """Metadata for generated image"""
    id: str
    filename: str
    prompt: str
    negative_prompt: str
    width: int
    height: int
    steps: int
    cfg_scale: float
    seed: Optional[int]
    workflow: Optional[str]
    category: str
    tags: List[str]
    status: GenerationStatus
    created_at: str
    completed_at: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageMetadata':
        data['status'] = GenerationStatus(data['status'])
        return cls(**data)


class ImageOrganizer:
    """Organize and manage generated images"""

    def __init__(self, base_dir: str = './generated_images'):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.images_dir = self.base_dir / 'images'
        self.images_dir.mkdir(exist_ok=True)

        self.metadata_file = self.base_dir / 'metadata.json'
        self.metadata: Dict[str, ImageMetadata] = {}
        self._load_metadata()

    def create_job(
        self,
        job_id: str,
        prompt: str,
        negative_prompt: str,
        parameters: Dict[str, Any],
        category: str = 'general',
        tags: List[str] = None
    ) -> ImageMetadata:
        """Create a new image generation job entry"""
        metadata = ImageMetadata(
            id=job_id,
            filename=f"{job_id}.png",
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=parameters.get('width', 1024),
            height=parameters.get('height', 1024),
            steps=parameters.get('steps', 30),
            cfg_scale=parameters.get('cfg_scale', 7.0),
            seed=parameters.get('seed'),
            workflow=parameters.get('workflow'),
            category=category,
            tags=tags or [],
            status=GenerationStatus.PENDING,
            created_at=datetime.now().isoformat()
        )

        self.metadata[job_id] = metadata
        self._save_metadata()
        return metadata

    def update_status(
        self,
        job_id: str,
        status: GenerationStatus,
        error: Optional[str] = None
    ) -> bool:
        """Update job status"""
        if job_id not in self.metadata:
            return False

        self.metadata[job_id].status = status
        if status == GenerationStatus.COMPLETED:
            self.metadata[job_id].completed_at = datetime.now().isoformat()
        if error:
            self.metadata[job_id].error = error

        self._save_metadata()
        return True

    def save_image(
        self,
        job_id: str,
        source_path: str,
        organize_by_category: bool = True
    ) -> Optional[str]:
        """Save generated image with optional category organization"""
        if job_id not in self.metadata:
            return None

        metadata = self.metadata[job_id]

        if organize_by_category:
            category_dir = self.images_dir / metadata.category
            category_dir.mkdir(exist_ok=True)
            dest_path = category_dir / metadata.filename
        else:
            dest_path = self.images_dir / metadata.filename

        try:
            shutil.copy2(source_path, dest_path)
            metadata.file_size = dest_path.stat().st_size
            self.update_status(job_id, GenerationStatus.COMPLETED)
            return str(dest_path)
        except Exception as e:
            self.update_status(job_id, GenerationStatus.FAILED, error=str(e))
            return None

    def get_image(self, job_id: str) -> Optional[ImageMetadata]:
        """Get image metadata by job ID"""
        return self.metadata.get(job_id)

    def list_images(
        self,
        category: Optional[str] = None,
        status: Optional[GenerationStatus] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[ImageMetadata]:
        """List images with optional filters"""
        results = list(self.metadata.values())

        if category:
            results = [img for img in results if img.category == category]

        if status:
            results = [img for img in results if img.status == status]

        if tags:
            results = [
                img for img in results
                if any(tag in img.tags for tag in tags)
            ]

        results.sort(key=lambda x: x.created_at, reverse=True)

        if limit:
            results = results[:limit]

        return results

    def search_images(self, query: str) -> List[ImageMetadata]:
        """Search images by prompt or tags"""
        query_lower = query.lower()
        results = []

        for img in self.metadata.values():
            if (query_lower in img.prompt.lower() or
                any(query_lower in tag.lower() for tag in img.tags)):
                results.append(img)

        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        total = len(self.metadata)
        by_status = {}
        by_category = {}

        for img in self.metadata.values():
            status_key = img.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            by_category[img.category] = by_category.get(img.category, 0) + 1

        completed = [
            img for img in self.metadata.values()
            if img.status == GenerationStatus.COMPLETED
        ]

        total_size = sum(img.file_size or 0 for img in completed)

        return {
            'total_jobs': total,
            'by_status': by_status,
            'by_category': by_category,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'completed_count': len(completed)
        }

    def export_metadata(self, job_id: str, output_path: str) -> bool:
        """Export metadata for specific image"""
        if job_id not in self.metadata:
            return False

        metadata = self.metadata[job_id]
        with open(output_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        return True

    def cleanup_failed(self) -> int:
        """Remove failed job entries"""
        failed = [
            job_id for job_id, img in self.metadata.items()
            if img.status == GenerationStatus.FAILED
        ]

        for job_id in failed:
            del self.metadata[job_id]

        if failed:
            self._save_metadata()

        return len(failed)

    def _load_metadata(self) -> None:
        """Load metadata from file"""
        if not self.metadata_file.exists():
            return

        with open(self.metadata_file, 'r') as f:
            data = json.load(f)
            self.metadata = {
                job_id: ImageMetadata.from_dict(img_data)
                for job_id, img_data in data.items()
            }

    def _save_metadata(self) -> None:
        """Save metadata to file"""
        data = {job_id: img.to_dict() for job_id, img in self.metadata.items()}
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)


class BatchProcessor:
    """Process multiple image generation requests"""

    def __init__(self, organizer: ImageOrganizer):
        self.organizer = organizer

    def create_batch(
        self,
        prompts: List[str],
        base_params: Dict[str, Any],
        category: str = 'batch',
        tags: List[str] = None
    ) -> List[str]:
        """Create batch of generation jobs"""
        job_ids = []

        for i, prompt in enumerate(prompts):
            job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            self.organizer.create_job(
                job_id=job_id,
                prompt=prompt,
                negative_prompt=base_params.get('negative_prompt', ''),
                parameters=base_params,
                category=category,
                tags=(tags or []) + ['batch']
            )

            job_ids.append(job_id)

        return job_ids

    def get_batch_status(self, batch_tag: str) -> Dict[str, int]:
        """Get status summary for batch"""
        images = self.organizer.list_images(tags=[batch_tag])

        status_count = {}
        for img in images:
            status_key = img.status.value
            status_count[status_key] = status_count.get(status_key, 0) + 1

        return status_count


if __name__ == '__main__':
    print("Image Organization System")
    organizer = ImageOrganizer()

    print("\nStatistics:")
    stats = organizer.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
