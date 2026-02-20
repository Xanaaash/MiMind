from fastapi import Body, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from modules.api.admin_endpoints import AdminAPI
from modules.api.billing_endpoints import BillingAPI
from modules.api.compliance_endpoints import DataGovernanceAPI
from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.observability_endpoints import ObservabilityAPI
from modules.api.prompt_endpoints import PromptRegistryAPI
from modules.api.safety_endpoints import SafetyAPI
from modules.api.scales_endpoints import ClinicalScalesAPI
from modules.api.tests_endpoints import InteractiveTestsAPI
from modules.api.tools_endpoints import HealingToolsAPI
from modules.onboarding.service import OnboardingService
from modules.storage import build_application_store

store = build_application_store()
admin_api = AdminAPI(store=store)
onboarding_api = OnboardingAPI(service=OnboardingService(store))
interactive_tests_api = InteractiveTestsAPI(store=store)
coach_api = CoachAPI(store=store)
healing_tools_api = HealingToolsAPI(store=store)
billing_api = BillingAPI(store=store)
compliance_api = DataGovernanceAPI(store=store)
safety_api = SafetyAPI(store=store)
scales_api = ClinicalScalesAPI()
prompt_api = PromptRegistryAPI()
observability_api = ObservabilityAPI(store=store)

app = FastAPI(
    title="MiMind Prototype API",
    version="0.1.0",
    description="Constitution-aligned prototype backend for MiMind",
)


def _unwrap(status: int, body: dict) -> dict:
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    return body.get("data", {})


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/api/admin/login")
def admin_login(response: Response, payload: dict = Body(...)) -> dict:
    status, body, session_id = admin_api.post_login(payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))

    if session_id:
        service = admin_api.service
        response.set_cookie(
            key=service.cookie_name(),
            value=session_id,
            max_age=service.cookie_max_age_seconds(),
            httponly=True,
            samesite=service.cookie_samesite(),
            secure=service.cookie_secure(),
            path=service.cookie_path(),
        )
    return body.get("data", {})


@app.post("/api/admin/logout")
def admin_logout(request: Request, response: Response) -> dict:
    session_id = request.cookies.get(admin_api.service.cookie_name())
    status, body = admin_api.post_logout(session_id=session_id)
    response.delete_cookie(key=admin_api.service.cookie_name(), path=admin_api.service.cookie_path())
    return _unwrap(status, body)


@app.get("/api/admin/session")
def admin_session(request: Request) -> dict:
    session_id = request.cookies.get(admin_api.service.cookie_name())
    status, body = admin_api.get_session(session_id=session_id)
    return _unwrap(status, body)


@app.get("/api/admin/users")
def admin_users(request: Request) -> JSONResponse:
    session_id = request.cookies.get(admin_api.service.cookie_name())
    status, body = admin_api.get_users(session_id=session_id)
    if status == 501:
        return JSONResponse(status_code=501, content=body.get("error", {}))
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    return JSONResponse(status_code=200, content=body.get("data", {}))


@app.post("/api/register")
def register(payload: dict = Body(...)) -> dict:
    status, body = onboarding_api.post_register(payload)
    return _unwrap(status, body)


@app.post("/api/assessment/{user_id}")
def submit_assessment(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = onboarding_api.post_assessment(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.get("/api/scales/catalog")
def get_scales_catalog() -> dict:
    status, body = scales_api.get_catalog()
    return _unwrap(status, body)


@app.post("/api/scales/score")
def score_single_clinical_scale(payload: dict = Body(...)) -> dict:
    status, body = scales_api.post_score_scale(payload)
    return _unwrap(status, body)


@app.get("/api/entitlements/{user_id}")
def get_entitlements(user_id: str) -> dict:
    status, body = onboarding_api.get_entitlements(user_id)
    return _unwrap(status, body)


@app.get("/api/reassessment/{user_id}")
def get_reassessment_schedule(user_id: str) -> dict:
    status, body = onboarding_api.get_reassessment_schedule(user_id)
    return _unwrap(status, body)


@app.get("/api/tests/catalog")
def get_tests_catalog() -> dict:
    status, body = interactive_tests_api.get_catalog()
    return _unwrap(status, body)


@app.get("/api/tests/catalog/{test_id}")
def get_test_catalog_item(test_id: str) -> dict:
    status, body = interactive_tests_api.get_catalog_item(test_id=test_id)
    return _unwrap(status, body)


@app.get("/api/prompts/packs")
def get_prompt_packs() -> dict:
    status, body = prompt_api.get_packs()
    return _unwrap(status, body)


@app.get("/api/prompts/active")
def get_active_prompt_pack() -> dict:
    status, body = prompt_api.get_active()
    return _unwrap(status, body)


@app.post("/api/prompts/activate")
def activate_prompt_pack(payload: dict = Body(...)) -> dict:
    status, body = prompt_api.post_activate(payload)
    return _unwrap(status, body)


@app.get("/api/observability/model-invocations")
def get_model_invocations(
    limit: int = Query(50, ge=1, le=500),
    task_type: str = Query("", alias="task_type"),
    provider: str = Query("", alias="provider"),
) -> list[dict]:
    normalized_task = task_type.strip() or None
    normalized_provider = provider.strip() or None
    status, body = observability_api.get_model_invocations(
        limit=limit,
        task_type=normalized_task,
        provider=normalized_provider,
    )
    return _unwrap(status, body)


@app.get("/api/observability/model-invocations/summary")
def get_model_invocation_summary(
    limit: int = Query(200, ge=1, le=2000),
    task_type: str = Query("", alias="task_type"),
    provider: str = Query("", alias="provider"),
) -> dict:
    normalized_task = task_type.strip() or None
    normalized_provider = provider.strip() or None
    status, body = observability_api.get_model_invocation_summary(
        limit=limit,
        task_type=normalized_task,
        provider=normalized_provider,
    )
    return _unwrap(status, body)


@app.post("/api/tests/{user_id}/submit")
def submit_test(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = interactive_tests_api.post_submit(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.get("/api/tests/{user_id}/report/{result_id}")
def get_test_report(user_id: str, result_id: str, subscription_active: bool = Query(False)) -> dict:
    status, body = interactive_tests_api.get_report(
        user_id=user_id,
        result_id=result_id,
        subscription_active=subscription_active,
    )
    return _unwrap(status, body)


@app.post("/api/tests/{user_id}/share/{result_id}")
def share_test_result(user_id: str, result_id: str) -> dict:
    status, body = interactive_tests_api.post_share_card(user_id=user_id, result_id=result_id)
    return _unwrap(status, body)


@app.post("/api/tests/pairing")
def test_pairing(payload: dict = Body(...)) -> dict:
    status, body = interactive_tests_api.post_pairing(payload)
    return _unwrap(status, body)


@app.post("/api/coach/{user_id}/start")
def start_coach_session(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = coach_api.post_start_session(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.post("/api/coach/{session_id}/chat")
def chat_with_coach(session_id: str, payload: dict = Body(...)) -> dict:
    status, body = coach_api.post_chat(session_id=session_id, payload=payload)
    return _unwrap(status, body)


@app.post("/api/coach/{session_id}/end")
def end_coach_session(session_id: str) -> dict:
    status, body = coach_api.post_end_session(session_id=session_id)
    return _unwrap(status, body)


@app.get("/api/tools/audio/library")
def get_audio_library() -> dict:
    status, body = healing_tools_api.get_audio_library()
    return _unwrap(status, body)


@app.post("/api/tools/audio/{user_id}/start")
def start_audio(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = healing_tools_api.post_start_audio(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.post("/api/tools/breathing/{user_id}/complete")
def complete_breathing(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = healing_tools_api.post_breathing_session(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.get("/api/tools/meditation/library")
def get_meditation_library() -> dict:
    status, body = healing_tools_api.get_meditation_library()
    return _unwrap(status, body)


@app.post("/api/tools/meditation/{user_id}/start")
def start_meditation(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = healing_tools_api.post_start_meditation(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.post("/api/tools/journal/{user_id}/entries")
def create_journal_entry(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = healing_tools_api.post_journal_entry(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.get("/api/tools/journal/{user_id}/entries")
def list_journal_entries(user_id: str) -> dict:
    status, body = healing_tools_api.get_journal_entries(user_id=user_id)
    return _unwrap(status, body)


@app.get("/api/tools/journal/{user_id}/trend")
def get_journal_trend(user_id: str, days: int = Query(7, ge=1, le=365)) -> dict:
    status, body = healing_tools_api.get_journal_trend(user_id=user_id, days=days)
    return _unwrap(status, body)


@app.get("/api/tools/{user_id}/stats")
def get_tools_usage_stats(user_id: str) -> dict:
    status, body = healing_tools_api.get_usage_stats(user_id=user_id)
    return _unwrap(status, body)


@app.get("/api/billing/plans")
def list_billing_plans() -> dict:
    status, body = billing_api.get_plans()
    return _unwrap(status, body)


@app.post("/api/billing/{user_id}/trial/start")
def start_trial(user_id: str) -> dict:
    status, body = billing_api.post_start_trial(user_id=user_id)
    return _unwrap(status, body)


@app.post("/api/billing/{user_id}/checkout")
def checkout(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = billing_api.post_checkout(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.post("/api/billing/webhook")
def billing_webhook(payload: dict = Body(...)) -> dict:
    status, body = billing_api.post_webhook(payload)
    return _unwrap(status, body)


@app.post("/api/billing/{user_id}/consume")
def consume_coach_quota(user_id: str) -> dict:
    status, body = billing_api.post_consume_coach_session(user_id=user_id)
    return _unwrap(status, body)


@app.get("/api/billing/{user_id}/subscription")
def get_subscription(user_id: str) -> dict:
    status, body = billing_api.get_subscription(user_id=user_id)
    return _unwrap(status, body)


@app.get("/api/billing/{user_id}/entitlements")
def get_billing_entitlements(user_id: str) -> dict:
    status, body = billing_api.get_entitlements(user_id=user_id)
    return _unwrap(status, body)


@app.post("/api/safety/{user_id}/assess")
def safety_assess(user_id: str, payload: dict = Body(...)) -> dict:
    status, body = safety_api.post_assess_message(user_id=user_id, payload=payload)
    return _unwrap(status, body)


@app.get("/api/safety/hotline-cache")
def safety_hotline_cache() -> dict:
    status, body = safety_api.get_hotline_cache()
    return _unwrap(status, body)


@app.get("/api/compliance/{user_id}/export")
def export_user_data(user_id: str) -> dict:
    status, body = compliance_api.get_export(user_id=user_id)
    return _unwrap(status, body)


@app.post("/api/compliance/{user_id}/erase")
def erase_user_data(user_id: str) -> dict:
    status, body = compliance_api.post_erase(user_id=user_id)
    return _unwrap(status, body)
