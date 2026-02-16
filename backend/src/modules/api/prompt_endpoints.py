from typing import Any, Dict, Optional, Tuple

from modules.prompt.registry.runtime import get_prompt_registry
from modules.prompt.registry.service import PromptRegistryService


class PromptRegistryAPI:
    def __init__(self, registry: Optional[PromptRegistryService] = None) -> None:
        self._registry = registry or get_prompt_registry()

    def get_packs(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._registry.list_packs()}

    def get_active(self) -> Tuple[int, Dict[str, Any]]:
        pack = self._registry.get_active_pack()
        return 200, {
            "data": {
                "active_version": self._registry.get_active_version(),
                "pack": pack.summary_dict(),
            }
        }

    def post_activate(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            version = str(payload.get("version", "")).strip()
            if not version:
                raise ValueError("version is required")

            activated = self._registry.activate(version=version)
            return 200, {
                "data": {
                    "active_version": activated.version,
                    "pack": activated.summary_dict(),
                }
            }
        except ValueError as error:
            return 400, {"error": str(error)}
