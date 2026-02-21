from modules.prompt.context.expert_qa import build_expert_qa_context
from modules.journal.context_adapter import build_journal_context_summary
from modules.prompt.context.neurodiversity import build_neurodiversity_scores
from modules.prompt.styles.neurodiversity import build_neurodiversity_prompt_fragments
from modules.storage.in_memory import InMemoryStore


def build_context_prompt(store: InMemoryStore, user_id: str) -> dict:
    user = store.get_user(user_id)
    if user is None:
        raise ValueError("Unknown user_id")

    scores = store.get_scores(user_id)
    triage = store.get_triage(user_id)
    memory_items = store.list_memory_summaries(user_id)[-3:]
    neurodiversity_scores = build_neurodiversity_scores(store, user_id)
    neurodiversity_prompt_fragments = build_neurodiversity_prompt_fragments(neurodiversity_scores)

    return {
        "user_profile": {
            "user_id": user.user_id,
            "email": user.email,
            "locale": user.locale,
        },
        "latest_assessment_scores": scores.to_dict() if scores else None,
        "latest_triage": triage.to_dict() if triage else None,
        "neurodiversity_scores": neurodiversity_scores,
        "neurodiversity_prompt_fragments": neurodiversity_prompt_fragments or None,
        "expert_qa": build_expert_qa_context(),
        "memory_summaries": memory_items,
        "journal_summary": build_journal_context_summary(store, user_id),
    }
