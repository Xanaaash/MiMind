from __future__ import annotations

import json
import re
from typing import Any, Dict, Mapping


_MAX_RAW_CHARS = 2000
_SENSITIVE_KEYS = {
    "password",
    "passcode",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "set-cookie",
    "secret",
    "api_key",
    "openai_api_key",
    "session_id",
    "email",
}
_EMAIL_PATTERN = re.compile(r"^([^@\s]+)@([^@\s]+)$")


def _truncate_text(value: str, max_chars: int = _MAX_RAW_CHARS) -> str:
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + "...(truncated)"


def _mask_email(value: str) -> str:
    matched = _EMAIL_PATTERN.match(value.strip())
    if not matched:
        return "***"
    local, domain = matched.groups()
    if len(local) <= 2:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def _mask_string(value: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        return "***"
    if _EMAIL_PATTERN.match(trimmed):
        return _mask_email(trimmed)
    if len(trimmed) <= 4:
        return "***"
    return f"{trimmed[:2]}***{trimmed[-2:]}"


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return sanitize_mapping(value)
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, str):
        return _truncate_text(value)
    return value


def sanitize_mapping(payload: Mapping[str, Any]) -> Dict[str, Any]:
    sanitized: Dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).strip().lower()
        if normalized in _SENSITIVE_KEYS:
            sanitized[str(key)] = _mask_string(str(value))
            continue
        sanitized[str(key)] = sanitize_payload(value)
    return sanitized


def decode_json_payload(raw_body: bytes) -> Dict[str, Any]:
    if not raw_body:
        return {}

    text = _truncate_text(raw_body.decode("utf-8", errors="ignore"))
    if not text:
        return {}

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}

    if isinstance(parsed, Mapping):
        return sanitize_mapping(parsed)
    if isinstance(parsed, list):
        return {"_list": sanitize_payload(parsed)}
    return {"_value": sanitize_payload(parsed)}
