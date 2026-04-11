import json
from pathlib import Path
from typing import Optional


class SettingsManager:
    SETTINGS_FILE = "settings.json"

    DEFAULT_SETTINGS = {
        "display_mode": "markdown",
    }

    def __init__(self):
        self._settings_path = Path(__file__).parent / self.SETTINGS_FILE
        self._settings: Optional[dict] = None

    def load(self) -> dict:
        if self._settings is not None:
            return self._settings

        if self._settings_path.exists():
            try:
                with open(self._settings_path, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
            except Exception:
                self._settings = self.DEFAULT_SETTINGS.copy()
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()

        return self._settings

    def save(self):
        if self._settings is not None:
            with open(self._settings_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        settings = self.load()
        return settings.get(key, default)

    def set(self, key: str, value):
        settings = self.load()
        settings[key] = value
        self._settings = settings
        self.save()
