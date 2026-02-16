from modules.storage.in_memory import InMemoryStore


class BreathingToolService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def build_478_pattern(self, cycles: int) -> dict:
        if cycles <= 0 or cycles > 20:
            raise ValueError("cycles must be between 1 and 20")

        steps = []
        for _ in range(cycles):
            steps.extend(
                [
                    {"phase": "inhale", "seconds": 4},
                    {"phase": "hold", "seconds": 7},
                    {"phase": "exhale", "seconds": 8},
                ]
            )

        total_seconds = sum(step["seconds"] for step in steps)
        return {
            "protocol": "4-7-8",
            "cycles": cycles,
            "total_seconds": total_seconds,
            "steps": steps,
        }

    def complete_session(self, user_id: str, cycles: int) -> dict:
        pattern = self.build_478_pattern(cycles)
        self._store.save_tool_event(
            user_id,
            {
                "tool": "breathing",
                "protocol": "4-7-8",
                "cycles": cycles,
                "total_seconds": pattern["total_seconds"],
            },
        )
        return pattern
