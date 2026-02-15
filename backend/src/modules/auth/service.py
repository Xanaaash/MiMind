import uuid

from modules.storage.in_memory import InMemoryStore
from modules.user.models import User


class AuthService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def register_user(self, email: str, locale: str) -> User:
        if not email or "@" not in email:
            raise ValueError("A valid email is required")
        if not locale:
            raise ValueError("locale is required")

        user = User(user_id=str(uuid.uuid4()), email=email.lower().strip(), locale=locale)
        self._store.save_user(user)
        return user
