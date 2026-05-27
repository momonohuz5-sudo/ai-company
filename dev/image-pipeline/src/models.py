"""Data models for the image production pipeline."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


@dataclass
class Work:
    """Represents a production work/project."""

    work_id: str
    title: str
    description: str
    created_at: str
    status: str = "planning"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Work":
        return cls(**data)

    @classmethod
    def create(cls, work_id: str, title: str, description: str = "") -> "Work":
        return cls(
            work_id=work_id,
            title=title,
            description=description,
            created_at=datetime.now().isoformat(),
            status="planning"
        )


@dataclass
class PromptBlock:
    """Represents a general prompt block (quality, character, setting, lighting, camera)."""

    block_id: str
    block_type: str
    content: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptBlock":
        return cls(**data)

    def validate(self) -> None:
        """Validate block data."""
        valid_types = ["quality", "character", "setting", "lighting", "camera"]
        if self.block_type not in valid_types:
            raise ValueError(f"Invalid block_type: {self.block_type}. Must be one of {valid_types}")

        if not self.content.strip():
            raise ValueError("Block content cannot be empty")

        if self.block_type == "quality" and not self.parameters:
            raise ValueError("Quality blocks must have parameters (steps, cfg_scale, etc.)")


@dataclass
class PrivateBlockRef:
    """OPAQUE reference to a private/negative block.

    This class never stores or accesses the actual content.
    Content is managed manually by the user in data/private/blocks/
    """

    block_id: str
    block_type: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivateBlockRef":
        return cls(**data)

    def validate(self) -> None:
        """Validate private block reference."""
        valid_types = ["private", "negative"]
        if self.block_type not in valid_types:
            raise ValueError(f"Invalid block_type: {self.block_type}. Must be one of {valid_types}")


@dataclass
class Scene:
    """Represents a single scene in a work."""

    work_id: str
    scene_no: int
    quality_id: str
    character_id: str
    setting_id: str
    lighting_id: str
    camera_id: str
    private_id: str
    negative_id: str
    seed: int
    output_dir: str
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        return cls(**data)

    def to_jsonl(self) -> str:
        """Convert to JSONL format (single line JSON)."""
        return json.dumps(self.to_dict())

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row."""
        return [
            self.work_id,
            str(self.scene_no),
            self.quality_id,
            self.character_id,
            self.setting_id,
            self.lighting_id,
            self.camera_id,
            self.private_id,
            self.negative_id,
            str(self.seed),
            self.output_dir,
            self.status
        ]

    @staticmethod
    def csv_headers() -> List[str]:
        """Get CSV headers."""
        return [
            "work_id",
            "scene_no",
            "quality_id",
            "character_id",
            "setting_id",
            "lighting_id",
            "camera_id",
            "private_id",
            "negative_id",
            "seed",
            "output_dir",
            "status"
        ]
