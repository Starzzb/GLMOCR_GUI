from PIL import Image
from pathlib import Path
from typing import Optional
import tempfile
import os


class ImageUtils:
    @staticmethod
    def ensure_rgb(image_path: str, output_path: Optional[str] = None) -> str:
        img = Image.open(image_path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)

        img.save(output_path)
        return output_path

    @staticmethod
    def is_pdf(file_path: str) -> bool:
        return Path(file_path).suffix.lower() == ".pdf"

    @staticmethod
    def get_image_info(image_path: str) -> dict:
        img = Image.open(image_path)
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
        }
