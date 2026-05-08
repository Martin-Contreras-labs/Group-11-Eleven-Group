from abc import ABC, abstractmethod


class AbstractCredentialStore(ABC):
    """Abstract base class for credential stores.

    This interface allows the credential store to be swapped for a
    database-backed implementation in future iterations without changing
    any code that depends on it (Dependency Inversion Principle).
    """

    @abstractmethod
    def is_valid(self, username: str, password: str) -> bool:
        """Return True if the username/password pair is valid."""
        ...

    @abstractmethod
    def list_credentials(self) -> dict[str, str]:
        """Return a copy of all stored credentials."""
        ...


class InMemoryCredentialStore(AbstractCredentialStore):
    """Simple in-memory credential store backed by a dictionary.

    Predefined credentials are loaded at construction time.
    In a future iteration this class can be replaced by a
    DatabaseCredentialStore that implements the same interface.
    """

    def __init__(self) -> None:
        self._credentials: dict[str, str] = {
            "hub_user_1": "Password123!",
            "hub_user_2": "Secure456!",
        }

    def is_valid(self, username: str, password: str) -> bool:
        stored = self._credentials.get(username)
        return stored is not None and stored == password

    def list_credentials(self) -> dict[str, str]:
        return dict(self._credentials)
