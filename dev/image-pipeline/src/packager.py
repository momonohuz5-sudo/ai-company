"""Output packaging and image renumbering."""

from pathlib import Path
from typing import List, Optional
import shutil
import zipfile

from .storage import Storage
from .logger import PrivacySafeLogger


class Packager:
    """Handles image renumbering and ZIP packaging."""

    def __init__(self, output_base_dir: Path, logger: PrivacySafeLogger):
        """Initialize packager.

        Args:
            output_base_dir: Base output directory
            logger: Logger instance
        """
        self.output_base_dir = output_base_dir
        self.logger = logger

    def renumber_images(
        self,
        work_id: str,
        start: int = 1,
        source_dir: str = "approved"
    ) -> List[Path]:
        """Renumber approved images sequentially.

        Args:
            work_id: Work identifier
            start: Starting number
            source_dir: Source directory name (approved, rejected, etc.)

        Returns:
            List of renumbered image paths
        """
        source_path = self.output_base_dir / work_id / source_dir
        package_dir = self.output_base_dir / work_id / "package" / "images"

        if not source_path.exists():
            self.logger.warning(f"Source directory not found: {source_path}")
            return []

        Storage.ensure_dir(package_dir)

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        source_images = sorted([
            f for f in source_path.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ])

        renumbered = []

        for idx, source_image in enumerate(source_images):
            number = start + idx
            dest_name = f"{number:03d}{source_image.suffix}"
            dest_path = package_dir / dest_name

            shutil.copy2(str(source_image), str(dest_path))
            renumbered.append(dest_path)

            self.logger.log_file_operation("renumbered", dest_path, success=True)

        self.logger.info(
            f"Renumbered {len(renumbered)} images for {work_id} "
            f"(start={start})"
        )

        return renumbered

    def separate_samples(
        self,
        work_id: str,
        sample_count: int = 5
    ) -> tuple[List[Path], List[Path]]:
        """Separate sample images from sales images.

        Args:
            work_id: Work identifier
            sample_count: Number of sample images to extract

        Returns:
            Tuple of (sample_paths, sales_paths)
        """
        package_images_dir = self.output_base_dir / work_id / "package" / "images"
        sample_dir = self.output_base_dir / work_id / "package" / "samples"
        sales_dir = self.output_base_dir / work_id / "package" / "sales"

        if not package_images_dir.exists():
            self.logger.warning(f"Package images directory not found: {package_images_dir}")
            return [], []

        Storage.ensure_dir(sample_dir)
        Storage.ensure_dir(sales_dir)

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        all_images = sorted([
            f for f in package_images_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ])

        sample_images = all_images[:sample_count]
        sales_images = all_images

        sample_paths = []
        for img in sample_images:
            dest_path = sample_dir / img.name
            shutil.copy2(str(img), str(dest_path))
            sample_paths.append(dest_path)

        sales_paths = []
        for img in sales_images:
            dest_path = sales_dir / img.name
            shutil.copy2(str(img), str(dest_path))
            sales_paths.append(dest_path)

        self.logger.info(
            f"Separated {len(sample_paths)} samples and {len(sales_paths)} sales images"
        )

        return sample_paths, sales_paths

    def create_package(
        self,
        work_id: str,
        compression: str = "deflate",
        include_metadata: bool = True
    ) -> Path:
        """Create ZIP package of approved images.

        Args:
            work_id: Work identifier
            compression: ZIP compression method
            include_metadata: Whether to include metadata.json

        Returns:
            Path to created ZIP file
        """
        package_dir = self.output_base_dir / work_id / "package"
        zip_path = package_dir / f"work_{work_id}.zip"

        if not package_dir.exists():
            raise FileNotFoundError(f"Package directory not found: {package_dir}")

        compression_map = {
            "deflate": zipfile.ZIP_DEFLATED,
            "stored": zipfile.ZIP_STORED,
            "bzip2": zipfile.ZIP_BZIP2,
            "lzma": zipfile.ZIP_LZMA
        }

        compression_type = compression_map.get(compression, zipfile.ZIP_DEFLATED)

        with zipfile.ZipFile(zip_path, 'w', compression_type) as zf:
            images_dir = package_dir / "images"
            if images_dir.exists():
                for img_file in images_dir.iterdir():
                    if img_file.is_file():
                        zf.write(img_file, f"images/{img_file.name}")

            samples_dir = package_dir / "samples"
            if samples_dir.exists():
                for img_file in samples_dir.iterdir():
                    if img_file.is_file():
                        zf.write(img_file, f"samples/{img_file.name}")

            sales_dir = package_dir / "sales"
            if sales_dir.exists():
                for img_file in sales_dir.iterdir():
                    if img_file.is_file():
                        zf.write(img_file, f"sales/{img_file.name}")

            if include_metadata:
                metadata_file = package_dir / "metadata.json"
                if metadata_file.exists():
                    zf.write(metadata_file, "metadata.json")

        self.logger.info(f"Package created: {zip_path.name}")

        return zip_path
