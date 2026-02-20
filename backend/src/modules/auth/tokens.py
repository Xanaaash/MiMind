import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Optional


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def encode_jwt(payload: Dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64url_encode(signature)}"


def decode_and_validate_jwt(token: str, secret: str, expected_token_type: Optional[str] = None) -> Dict[str, object]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".", 2)
    except ValueError as error:
        raise ValueError("Invalid token format") from error

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        decoded_signature = _b64url_decode(signature_segment)
    except Exception as error:  # pragma: no cover - defensive parse guard
        raise ValueError("Invalid token signature") from error

    if not hmac.compare_digest(decoded_signature, expected_signature):
        raise ValueError("Invalid token signature")

    try:
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    except Exception as error:  # pragma: no cover - defensive parse guard
        raise ValueError("Invalid token payload") from error

    if not isinstance(payload, dict):
        raise ValueError("Invalid token payload")

    now = int(time.time())
    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise ValueError("Token missing expiry")
    if exp <= now:
        raise ValueError("Token expired")

    token_type = payload.get("token_type")
    if expected_token_type and token_type != expected_token_type:
        raise ValueError("Invalid token type")

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise ValueError("Token missing subject")

    return payload
