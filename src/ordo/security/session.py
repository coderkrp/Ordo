"""Session management for broker adapters."""

from cryptography.fernet import Fernet
from ordo.config import settings


class SessionManager:
    """Manages encrypted session data for broker adapters."""

    def __init__(self):
        if not settings.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set for session management.")
        self._fernet = Fernet(settings.SECRET_KEY.encode())
        self._sessions = {}

    def _get_namespaced_key(self, broker_id: str, key: str) -> str:
        """Creates a namespaced key to prevent collisions."""
        return f"{broker_id}:{key}"

    def set_session(self, broker_id: str, key: str, value: str):
        """
        Encrypts and stores a session value for a given broker.
        """
        namespaced_key = self._get_namespaced_key(broker_id, key)
        encrypted_value = self._fernet.encrypt(value.encode())
        self._sessions[namespaced_key] = encrypted_value

    def get_session(self, broker_id: str, key: str) -> str | None:
        """
        Retrieves and decrypts a session value for a given broker.
        """
        namespaced_key = self._get_namespaced_key(broker_id, key)
        encrypted_value = self._sessions.get(namespaced_key)
        if not encrypted_value:
            return None
        decrypted_value = self._fernet.decrypt(encrypted_value).decode()
        return decrypted_value
