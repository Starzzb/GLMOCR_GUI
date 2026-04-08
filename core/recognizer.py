from pathlib import Path
from typing import Optional
import json
import requests
from .config_manager import ConfigManager


class GLMRecognizer:
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager(config_path)
        self._client = None

    def recognize(self, file_path: str) -> dict:
        config = self.config_manager.load()
        api_config = config.get("pipeline", {}).get("ocr_api", {})

        api_host = api_config.get("api_host", "localhost")
        api_port = api_config.get("api_port", 11434)
        api_path = api_config.get("api_path", "/api/generate")
        model = api_config.get("model", "glm-ocr:latest")
        api_mode = api_config.get("api_mode", "ollama_generate")

        base_url = f"http://{api_host}:{api_port}"

        with open(file_path, "rb") as f:
            image_data = f.read()

        import base64

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        if api_mode == "ollama_generate":
            payload = {
                "model": model,
                "prompt": "请识别图片中的文字内容，以Markdown格式输出",
                "images": [image_b64],
                "stream": False,
            }
            response = requests.post(f"{base_url}{api_path}", json=payload, timeout=120)
            response.raise_for_status()
            result_text = response.json().get("response", "")
        else:
            raise ValueError(f"Unsupported API mode: {api_mode}")

        return {
            "markdown": result_text,
            "json": [],
            "raw_text": result_text,
            "metadata": {"pages": 1, "confidence": None},
        }
