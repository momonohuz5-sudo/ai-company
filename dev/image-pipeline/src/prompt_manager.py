"""Prompt block management with privacy-safe design."""

from pathlib import Path
from typing import List, Optional
import uuid

from .models import PromptBlock, PrivateBlockRef
from .storage import Storage
from .logger import PrivacySafeLogger


class PromptManager:
    """Manages prompt blocks (general and private refs)."""

    def __init__(self, blocks_base_dir: Path, private_dir: Path, logger: PrivacySafeLogger):
        """Initialize prompt manager.

        Args:
            blocks_base_dir: Base directory for general blocks
            private_dir: Directory for private blocks (NEVER accessed by tool)
            logger: Logger instance
        """
        self.blocks_base_dir = blocks_base_dir
        self.private_dir = private_dir
        self.logger = logger

        for block_type in ["quality", "character", "setting", "lighting", "camera"]:
            Storage.ensure_dir(blocks_base_dir / block_type)

        Storage.ensure_dir(private_dir / "blocks")

    def create_block(
        self,
        block_type: str,
        content: str,
        parameters: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        block_id: Optional[str] = None
    ) -> PromptBlock:
        """Create a general prompt block.

        Args:
            block_type: Block type (quality, character, setting, lighting, camera)
            content: Block content (prompt text)
            parameters: Parameters dict (for quality: steps, cfg_scale, etc.)
            tags: Tags for categorization
            block_id: Optional custom block ID (generated if not provided)

        Returns:
            Created PromptBlock instance

        Raises:
            ValueError: If block_type is invalid or content is empty
        """
        if block_id is None:
            block_id = f"{block_type}_{uuid.uuid4().hex[:8]}"

        block = PromptBlock(
            block_id=block_id,
            block_type=block_type,
            content=content,
            parameters=parameters or {},
            tags=tags or []
        )

        block.validate()

        block_file = self.blocks_base_dir / block_type / f"{block_id}.json"

        if block_file.exists():
            raise ValueError(f"Block already exists: {block_id}")

        Storage.save_json(block_file, block.to_dict())

        self.logger.info(f"Block created: {block_id} (type={block_type})")

        return block

    def get_block(self, block_id: str, block_type: str) -> PromptBlock:
        """Get block by ID and type.

        Args:
            block_id: Block identifier
            block_type: Block type

        Returns:
            PromptBlock instance

        Raises:
            FileNotFoundError: If block doesn't exist
        """
        block_file = self.blocks_base_dir / block_type / f"{block_id}.json"

        if not block_file.exists():
            raise FileNotFoundError(f"Block not found: {block_id} (type={block_type})")

        data = Storage.load_json(block_file)
        return PromptBlock.from_dict(data)

    def list_blocks(self, block_type: str) -> List[PromptBlock]:
        """List blocks by type.

        Args:
            block_type: Block type to list

        Returns:
            List of PromptBlock instances
        """
        blocks_dir = self.blocks_base_dir / block_type

        if not blocks_dir.exists():
            return []

        block_files = Storage.list_json_files(blocks_dir)
        blocks = []

        for block_file in block_files:
            try:
                data = Storage.load_json(block_file)
                blocks.append(PromptBlock.from_dict(data))
            except Exception as e:
                self.logger.error(
                    f"Failed to load block from {block_file.name}: {type(e).__name__}"
                )

        return sorted(blocks, key=lambda b: b.created_at, reverse=True)

    def create_private_ref(self, block_type: str, block_id: Optional[str] = None) -> PrivateBlockRef:
        """Create OPAQUE reference to a private/negative block.

        Args:
            block_type: Block type (private or negative)
            block_id: Optional custom block ID

        Returns:
            PrivateBlockRef instance (ID only, no content)

        Privacy Note:
            This method creates a marker file only.
            User must manually create/edit the actual JSON file at:
            data/private/blocks/{block_id}.json
        """
        if block_id is None:
            block_id = f"{block_type}_{uuid.uuid4().hex[:8]}"

        ref = PrivateBlockRef(block_id=block_id, block_type=block_type)
        ref.validate()

        marker_file = self.private_dir / "blocks" / f"{block_id}.marker"
        Storage.create_marker_file(marker_file)

        self.logger.info(
            f"Private block reference created: {block_id} (type={block_type}). "
            f"User must manually create: data/private/blocks/{block_id}.json"
        )

        return ref

    def validate_block_exists(self, block_id: str, block_type: str) -> bool:
        """Validate that a block exists (file check only, no content read).

        Args:
            block_id: Block identifier
            block_type: Block type

        Returns:
            True if block file exists

        Privacy Note:
            For private/negative blocks, this only checks marker file existence.
            Does NOT read or validate actual private content.
        """
        if block_type in ["private", "negative"]:
            marker_file = self.private_dir / "blocks" / f"{block_id}.marker"
            exists = Storage.file_exists(marker_file)
        else:
            block_file = self.blocks_base_dir / block_type / f"{block_id}.json"
            exists = Storage.file_exists(block_file)

        self.logger.log_block_validation(block_id, exists)

        return exists
