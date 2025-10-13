"""Session management for broker adapters."""

from cryptography.fernet import Fernet


class SessionCheckResult:
    """Result of session validation check."""

    def __init__(self, status: str, message: str = ""):
        self.status = status  # "valid", "expired", "refresh_failed", "unsupported"
        self.message = message


class SessionManager:
    """Manages encrypted session data for broker adapters."""

    def __init__(self, secret_key: str):
        if not secret_key:
            raise ValueError("SECRET_KEY must be provided for session management.")
        self._fernet = Fernet(secret_key.encode())
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

    async def ensure_valid_session(
        self, broker_id: str, account_id: str
    ) -> SessionCheckResult:
        """
        Validate session before orchestrator makes broker calls.

        Args:
            broker_id: Broker identifier
            account_id: Account identifier for the broker

        Returns:
            SessionCheckResult with status:
            - "valid": Session exists and is valid
            - "expired": Session expired
            - "refresh_failed": Session refresh attempted but failed
            - "unsupported": Broker doesn't support session refresh
        """
        # Check if session exists
        session_token = self.get_session(broker_id, "access_token")

        if session_token:
            # Session exists, assume it's valid for now
            # In a real implementation, we would check expiry time
            return SessionCheckResult(status="valid", message="Session is valid")

        # No session found
        return SessionCheckResult(
            status="expired", message=f"No session found for broker {broker_id}"
        )
