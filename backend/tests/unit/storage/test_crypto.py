import os
import unittest
from hashlib import sha256

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.security.crypto import DataEncryptor, EncryptionConfig


class DataEncryptionUnitTests(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self) -> None:
        key = sha256(b"unit-test-key").digest()
        encryptor = DataEncryptor(EncryptionConfig(key_bytes=key, source="unit-test"))
        payload = {"message": "hello", "count": 3, "nested": {"ok": True}}

        encrypted = encryptor.encrypt_json(payload)
        self.assertTrue(encrypted.startswith("enc:v1:"))

        decrypted = encryptor.decrypt_json(encrypted)
        self.assertEqual(decrypted, payload)

    def test_decrypt_legacy_plain_json_payload(self) -> None:
        key = sha256(b"unit-test-key").digest()
        encryptor = DataEncryptor(EncryptionConfig(key_bytes=key, source="unit-test"))
        plaintext = '{"legacy":"json"}'
        self.assertEqual(encryptor.decrypt_json(plaintext), {"legacy": "json"})

    def test_invalid_key_from_env_raises(self) -> None:
        original = os.environ.get("MIMIND_DATA_ENCRYPTION_KEY")
        try:
            os.environ["MIMIND_DATA_ENCRYPTION_KEY"] = "invalid-key"
            with self.assertRaises(ValueError):
                EncryptionConfig.from_env()
        finally:
            if original is None:
                os.environ.pop("MIMIND_DATA_ENCRYPTION_KEY", None)
            else:
                os.environ["MIMIND_DATA_ENCRYPTION_KEY"] = original


if __name__ == "__main__":
    unittest.main()
