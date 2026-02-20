import os
from typing import Optional


DEFAULT_MEDIA_ASSET_BASE_URL = "/audio"


class MediaAssetURLBuilder:
    def __init__(self, base_url: Optional[str] = None) -> None:
        resolved = (base_url or os.getenv("MEDIA_ASSET_BASE_URL") or DEFAULT_MEDIA_ASSET_BASE_URL).strip()
        self._base_url = resolved.rstrip("/")

    @property
    def base_url(self) -> str:
        return self._base_url

    def build(self, asset_path: str) -> str:
        normalized = asset_path.strip().lstrip("/")
        if not normalized:
            raise ValueError("asset_path is required")

        if self._base_url.startswith("http://") or self._base_url.startswith("https://"):
            return f"{self._base_url}/{normalized}"

        if self._base_url.startswith("/"):
            return f"{self._base_url}/{normalized}"

        return f"/{self._base_url}/{normalized}"
