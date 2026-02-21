import json
import time
from typing import Optional
from uuid import uuid4

from fastapi import Body, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from modules.api.admin_endpoints import AdminAPI
from modules.api.auth_endpoints import UserAuthAPI
from modules.api.billing_endpoints import BillingAPI
from modules.api.compliance_endpoints import DataGovernanceAPI
from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.observability_endpoints import ObservabilityAPI
from modules.api.prompt_endpoints import PromptRegistryAPI
from modules.api.rate_limit import APIRateLimiter, RateLimitConfig
from modules.api.safety_endpoints import SafetyAPI
from modules.api.scales_endpoints import ClinicalScalesAPI
from modules.api.tests_endpoints import InteractiveTestsAPI
from modules.api.tools_endpoints import HealingToolsAPI
from modules.onboarding.service import OnboardingService
from modules.observability.http_audit import decode_json_payload, sanitize_mapping
from modules.observability.models import APIAuditLogRecord
from modules.storage import build_application_store

store = build_application_store()
admin_api = AdminAPI(store=store)
onboarding_service = OnboardingService(store)
onboarding_api = OnboardingAPI(service=onboarding_service)
user_auth_api = UserAuthAPI(store=store, onboarding_service=onboarding_service)
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

api_rate_limiter = APIRateLimiter(config=RateLimitConfig.from_env())


def _unwrap(status: int, body: dict) -> dict:
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    return body.get("data", {})


def _extract_user_id_from_request(request: Request) -> Optional[str]:
    explicit_user = request.headers.get("x-user-id", "").strip()
    if explicit_user:
        return explicit_user[:128]

    path_parts = request.url.path.strip("/").split("/")
    if len(path_parts) >= 3 and path_parts[0] == "api":
        if path_parts[1] in {"assessment", "entitlements", "reassessment", "billing", "tools", "compliance"}:
            return path_parts[2][:128]
        if path_parts[1] == "coach" and len(path_parts) >= 4 and path_parts[3] in {"start", "sessions"}:
            return path_parts[2][:128]
    return None


def _set_user_auth_cookies(response: Response, tokens) -> None:
    service = user_auth_api.service
    response.set_cookie(
        key=service.access_cookie_name(),
        value=tokens.access_token,
        max_age=service.access_cookie_max_age_seconds(),
        httponly=True,
        samesite=service.cookie_samesite(),
        secure=service.cookie_secure(),
        path=service.cookie_path(),
    )
    response.set_cookie(
        key=service.refresh_cookie_name(),
        value=tokens.refresh_token,
        max_age=service.refresh_cookie_max_age_seconds(),
        httponly=True,
        samesite=service.cookie_samesite(),
        secure=service.cookie_secure(),
        path=service.cookie_path(),
    )


def _clear_user_auth_cookies(response: Response) -> None:
    service = user_auth_api.service
    response.delete_cookie(key=service.access_cookie_name(), path=service.cookie_path())
    response.delete_cookie(key=service.refresh_cookie_name(), path=service.cookie_path())


@app.middleware("http")
async def enforce_api_rate_limit(request: Request, call_next):
    if not request.url.path.startswith("/api/") or not api_rate_limiter.enabled:
        return await call_next(request)

    decision = api_rate_limiter.evaluate(request)
    if not decision.allowed:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"},
            headers={
                "Retry-After": str(decision.retry_after_seconds),
                "X-RateLimit-Limit": str(decision.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Scope": decision.scope,
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(decision.limit)
    response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
    response.headers["X-RateLimit-Scope"] = decision.scope
    return response


@app.middleware("http")
async def audit_api_requests(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    started = time.perf_counter()
    request_body = await request.body()
    request_payload = {"query": sanitize_mapping(dict(request.query_params))}
    if request_body:
        request_payload["body"] = decode_json_payload(request_body)

    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000

    response_payload = {}
    if isinstance(response, StreamingResponse):
        response_payload = {"_streaming": True}
    else:
        body = getattr(response, "body", b"") or b""
        if isinstance(body, str):
            body = body.encode("utf-8", errors="ignore")
        if isinstance(body, (bytes, bytearray)) and body:
            response_payload = decode_json_payload(bytes(body))

    client_ref = request.client.host if request.client is not None else None
    record = APIAuditLogRecord(
        request_id=uuid4().hex,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=elapsed_ms,
        request_payload=request_payload,
        response_payload=response_payload,
        user_id=_extract_user_id_from_request(request),
        client_ref=client_ref,
    )
    try:
        store.save_api_audit_log(record)
    except Exception:
        pass

    return response


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


@app.post("/api/auth/register")
def auth_register(response: Response, payload: dict = Body(...)) -> dict:
    status, body, tokens = user_auth_api.post_register(payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    if tokens is not None:
        _set_user_auth_cookies(response, tokens)
    response.status_code = status
    return body.get("data", {})


@app.post("/api/auth/login")
def auth_login(response: Response, payload: dict = Body(...)) -> dict:
    status, body, tokens = user_auth_api.post_login(payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    if tokens is not None:
        _set_user_auth_cookies(response, tokens)
    return body.get("data", {})


@app.get("/api/auth/session")
def auth_session(request: Request) -> dict:
    access_token = request.cookies.get(user_auth_api.service.access_cookie_name())
    status, body = user_auth_api.get_session(access_token=access_token)
    return _unwrap(status, body)


@app.post("/api/auth/refresh")
def auth_refresh(request: Request, response: Response) -> dict:
    refresh_token = request.cookies.get(user_auth_api.service.refresh_cookie_name())
    status, body, tokens = user_auth_api.post_refresh(refresh_token=refresh_token)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))
    if tokens is not None:
        _set_user_auth_cookies(response, tokens)
    return body.get("data", {})


@app.post("/api/auth/logout")
def auth_logout(response: Response) -> dict:
    status, body = user_auth_api.post_logout()
    _clear_user_auth_cookies(response)
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


@app.get("/api/observability/http-audit")
def get_http_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    method: str = Query("", alias="method"),
    path: str = Query("", alias="path"),
    status_code: int = Query(0, alias="status_code"),
    user_id: str = Query("", alias="user_id"),
) -> list[dict]:
    normalized_method = method.strip() or None
    normalized_path = path.strip() or None
    normalized_user = user_id.strip() or None
    normalized_status = status_code if status_code > 0 else None
    status, body = observability_api.get_api_audit_logs(
        limit=limit,
        method=normalized_method,
        path=normalized_path,
        status_code=normalized_status,
        user_id=normalized_user,
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


@app.post("/api/coach/{session_id}/chat/stream")
def stream_chat_with_coach(session_id: str, payload: dict = Body(...)) -> StreamingResponse:
    status, body = coach_api.post_chat_stream(session_id=session_id, payload=payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=body.get("error", "request failed"))

    data = body.get("data", {})
    coach_message = str(data.get("coach_message", ""))

    def _sse_event(event: str, content: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(content, ensure_ascii=False)}\n\n"

    def _stream():
        yield _sse_event(
            "meta",
            {
                "mode": data.get("mode"),
                "halted": data.get("halted"),
            },
        )

        chunk_size = 4
        for index in range(0, len(coach_message), chunk_size):
            chunk = coach_message[index:index + chunk_size]
            yield _sse_event(
                "token",
                {
                    "delta": chunk,
                    "index": index // chunk_size,
                },
            )

        yield _sse_event(
            "done",
            {
                "coach_message": coach_message,
                "triage": data.get("triage"),
                "safety": data.get("safety"),
                "model": data.get("model"),
                "mode": data.get("mode"),
                "halted": data.get("halted"),
            },
        )

    return StreamingResponse(_stream(), media_type="text/event-stream")


@app.post("/api/coach/{session_id}/end")
def end_coach_session(session_id: str) -> dict:
    status, body = coach_api.post_end_session(session_id=session_id)
    return _unwrap(status, body)


@app.get("/api/coach/{user_id}/sessions")
def list_coach_sessions(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    status, body = coach_api.get_session_history(user_id=user_id, limit=limit)
    return _unwrap(status, body)


@app.get("/api/coach/{user_id}/sessions/{session_id}")
def get_coach_session_summary(user_id: str, session_id: str) -> dict:
    status, body = coach_api.get_session_summary(user_id=user_id, session_id=session_id)
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
