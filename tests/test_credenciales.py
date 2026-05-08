from cleverhome.credenciales import CredentialStore

# 1. Valid credentials
def test_valid_credentials() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    result = store.is_valid("hub_user_1", "Password123!")
    # Assert
    assert result is True

# 2. Invalid password
def test_invalid_password() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    result = store.is_valid("hub_user_1", "wrongpassword")
    # Assert
    assert result is False

# 3. Unknown username
def test_unknown_username() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    result = store.is_valid("unknown_user", "Password123!")
    # Assert
    assert result is False

# 4. List credentials returns all usernames
def test_list_credentials() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    credentials = store.list_credentials()
    # Assert
    assert "hub_user_1" in credentials
    assert "hub_user_2" in credentials

# 5. Empty username
def test_empty_username() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    result = store.is_valid("", "Password123!")
    # Assert
    assert result is False

# 6. Empty password
def test_empty_password() -> None:
    # Arrange
    store = CredentialStore()
    # Act
    result = store.is_valid("hub_user_1", "")
    # Assert
    assert result is False