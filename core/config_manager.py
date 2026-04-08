import yaml
from pathlib import Path
from typing import Optional


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "default_config.yaml"
        self.config_path = Path(config_path)
        self._config: Optional[dict] = None

    def load(self) -> dict:
        if self._config is not None:
            return self._config

        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self._get_default_config()

        return self._config

    def _get_default_config(self) -> dict:
        return {
            "pipeline": {
                "maas": {"enabled": False},
                "ocr_api": {
                    "api_host": "localhost",
                    "api_port": 11434,
                    "api_path": "/api/generate",
                    "model": "glm-ocr:latest",
                    "api_mode": "ollama_generate",
                },
            },
            "ocr": {"use_pdf_pipeline": True, "max_pages": 100, "timeout": 120},
        }

    def get(self, key: str, default=None):
        config = self.load()
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
