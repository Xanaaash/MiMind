from typing import Dict, Optional

from modules.prompt.registry.catalog import PROMPT_PACKS
from modules.prompt.registry.models import PromptPack


class PromptRegistryService:
    def __init__(
        self,
        packs: Optional[Dict[str, PromptPack]] = None,
        default_active_version: Optional[str] = None,
    ) -> None:
        self._packs = dict(packs or PROMPT_PACKS)
        if not self._packs:
            raise ValueError("Prompt pack catalog must not be empty")

        latest = sorted(self._packs.keys())[-1]
        if default_active_version and default_active_version in self._packs:
            self._active_version = default_active_version
        else:
            self._active_version = latest

    def list_packs(self) -> Dict[str, dict]:
        return {
            version: pack.summary_dict()
            for version, pack in sorted(self._packs.items(), key=lambda item: item[0])
        }

    def get_active_version(self) -> str:
        return self._active_version

    def get_active_pack(self) -> PromptPack:
        return self._packs[self._active_version]

    def activate(self, version: str) -> PromptPack:
        normalized = str(version).strip()
        if normalized not in self._packs:
            raise ValueError(f"Unknown prompt version: {normalized}")
        self._active_version = normalized
        return self._packs[self._active_version]

    def get_system_prompt(self, version: Optional[str] = None) -> str:
        return self._get_pack(version).system_prompt

    def get_style_prompt(self, style_id: str, version: Optional[str] = None) -> dict:
        pack = self._get_pack(version)
        style = pack.style_prompts.get(style_id)
        if style is None:
            raise ValueError(f"Unsupported style_id: {style_id}")
        return dict(style)

    def _get_pack(self, version: Optional[str]) -> PromptPack:
        if version is None:
            return self.get_active_pack()

        normalized = str(version).strip()
        pack = self._packs.get(normalized)
        if pack is None:
            raise ValueError(f"Unknown prompt version: {normalized}")
        return pack
