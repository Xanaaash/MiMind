from modules.storage.in_memory import InMemoryStore


def build_journal_context_summary(store: InMemoryStore, user_id: str, limit: int = 7) -> dict:
    entries = store.list_journal_entries(user_id)
    if not entries:
        return {
            "entry_count": 0,
            "latest_mood": None,
            "average_energy": None,
        }

    sliced = entries[-limit:]
    avg_energy = sum(entry.energy for entry in sliced) / len(sliced)
    latest = sliced[-1]

    return {
        "entry_count": len(sliced),
        "latest_mood": latest.mood,
        "average_energy": round(avg_energy, 2),
    }
