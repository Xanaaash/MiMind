from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


_DEFAULT_DEV_KEY_SEED = "mimind-dev-aes256-key"
_KEY_ENV_NAME = "MIMIND_DATA_ENCRYPTION_KEY"
_ENVELOPE_PREFIX = "enc:v1"


@dataclass(frozen=True)
class EncryptionConfig:
    key_bytes: bytes
    source: str

    @staticmethod
    def from_env() -> "EncryptionConfig":
        raw = os.getenv(_KEY_ENV_NAME, "").strip()
        if raw:
            parsed = _parse_key_material(raw)
            return EncryptionConfig(key_bytes=parsed, source=_KEY_ENV_NAME)

        # Dev-safe fallback keeps local environments bootable.
        fallback = sha256(_DEFAULT_DEV_KEY_SEED.encode("utf-8")).digest()
        return EncryptionConfig(key_bytes=fallback, source="dev-fallback")


def _parse_key_material(raw: str) -> bytes:
    candidate = raw
    if candidate.startswith("base64:"):
        candidate = candidate.split(":", 1)[1]

    try:
        decoded = base64.b64decode(candidate.encode("ascii"), validate=True)
        if len(decoded) == 32:
            return decoded
    except Exception:
        pass

    if len(candidate) == 64:
        try:
            decoded_hex = bytes.fromhex(candidate)
            if len(decoded_hex) == 32:
                return decoded_hex
        except ValueError:
            pass

    raise ValueError(
        f"{_KEY_ENV_NAME} must be 32 bytes (base64 or 64-char hex) for AES-256 encryption"
    )


class DataEncryptor:
    def __init__(self, config: EncryptionConfig) -> None:
        self._config = config
        self._cipher = AESGCM(config.key_bytes)

    @staticmethod
    def from_env() -> "DataEncryptor":
        return DataEncryptor(EncryptionConfig.from_env())

    @property
    def key_source(self) -> str:
        return self._config.source

    def encrypt_json(self, payload: Any) -> str:
        plaintext = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        nonce = os.urandom(12)
        ciphertext = self._cipher.encrypt(nonce, plaintext, associated_data=None)
        nonce_b64 = base64.b64encode(nonce).decode("ascii")
        ciphertext_b64 = base64.b64encode(ciphertext).decode("ascii")
        return f"{_ENVELOPE_PREFIX}:{nonce_b64}:{ciphertext_b64}"

    def decrypt_json(self, envelope: str) -> Any:
        if not isinstance(envelope, str) or not envelope:
            raise ValueError("Encrypted payload is required")

        if not envelope.startswith(f"{_ENVELOPE_PREFIX}:"):
            # Backward compatibility for legacy plaintext rows.
            return json.loads(envelope)

        parts = envelope.split(":", 3)
        if len(parts) != 4:
            raise ValueError("Invalid encrypted payload format")

        nonce = base64.b64decode(parts[2].encode("ascii"))
        ciphertext = base64.b64decode(parts[3].encode("ascii"))
        plaintext = self._cipher.decrypt(nonce, ciphertext, associated_data=None)
        return json.loads(plaintext.decode("utf-8"))
