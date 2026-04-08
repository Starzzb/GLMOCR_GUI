from pathlib import Path
from typing import Tuple, Optional


class FileValidator:
    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    MAX_PDF_SIZE = 50 * 1024 * 1024

    @classmethod
    def validate(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        path = Path(file_path)

        if not path.exists():
            return False, "文件不存在"

        ext = path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return (
                False,
                f"不支持的格式: {ext}\n支持: {', '.join(cls.SUPPORTED_EXTENSIONS)}",
            )

        file_size = path.stat().st_size
        if ext == ".pdf":
            if file_size > cls.MAX_PDF_SIZE:
                return False, f"PDF文件过大 ({file_size / 1024 / 1024:.1f}MB > 50MB)"
        else:
            if file_size > cls.MAX_IMAGE_SIZE:
                return False, f"图片文件过大 ({file_size / 1024 / 1024:.1f}MB > 10MB)"

        return True, None
