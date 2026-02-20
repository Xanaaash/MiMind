import hashlib
import hmac
import re
import secrets


_PASSWORD_MIN_LEN = 8
_PBKDF2_ROUNDS = 150_000


def validate_password_strength(password: str) -> None:
    if len(password) < _PASSWORD_MIN_LEN:
        raise ValueError("Password must be at least 8 characters")
    if re.search(r"[A-Za-z]", password) is None:
        raise ValueError("Password must contain letters")
    if re.search(r"[0-9]", password) is None:
        raise ValueError("Password must contain digits")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds_raw, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds_raw)
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(candidate, expected_digest)
