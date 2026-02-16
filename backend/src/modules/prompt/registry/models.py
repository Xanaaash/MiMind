from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PromptPack:
    version: str
    system_prompt: str
    style_prompts: Dict[str, dict]
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "system_prompt": self.system_prompt,
            "style_prompts": {key: dict(value) for key, value in self.style_prompts.items()},
            "note": self.note,
        }

    def summary_dict(self) -> dict:
        return {
            "version": self.version,
            "style_ids": sorted(self.style_prompts.keys()),
            "note": self.note,
        }
