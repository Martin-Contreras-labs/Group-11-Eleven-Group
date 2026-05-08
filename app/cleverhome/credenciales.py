class CredentialStore:
    def __init__(self) -> None:
        self._credentials: dict[str, str] = {
            "hub_user_1": "Password123!",
            "hub_user_2": "Secure456!",
        }

    def is_valid(self, username: str, password: str) -> bool:
        stored_password = self._credentials.get(username)
        return stored_password == password

    def list_credentials(self) -> dict[str, str]:
        return dict(self._credentials)