"""Unit tests for the CleverHome Platform.

All tests follow the Arrange / Act / Assert structure.
Tests are grouped by module: protocol, credential_store, hub_server.
"""

import pytest
import socket

from cleverhome.hub_server import ConnectedHub, HubServer
from cleverhome.protocol import (
    Message,
    MessageType,
    ProtocolError,
    build_acc,
    build_err,
    build_gs,
    build_ok,
    build_ref,
    build_ss,
    parse_message,
    serialize_message,
)
from cleverhome.credential_store import InMemoryCredentialStore


# ════════════════════════════════════════════════════════════════════════════
# PROTOCOL — parse_message
# ════════════════════════════════════════════════════════════════════════════

class TestParseMessage:

    def test_parse_gs_no_params(self) -> None:
        # Arrange
        raw = "GS."
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.GS
        assert msg.parameters == {}

    def test_parse_acc_no_params(self) -> None:
        # Arrange
        raw = "ACC."
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.ACC
        assert msg.parameters == {}

    def test_parse_hl_with_all_params(self) -> None:
        # Arrange
        raw = "HL:USR=hub_user_1;PWD=Password123!;HOM=home1;TT=20."
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.HL
        assert msg.parameters["USR"] == "hub_user_1"
        assert msg.parameters["PWD"] == "Password123!"
        assert msg.parameters["HOM"] == "home1"
        assert msg.parameters["TT"] == "20"

    def test_parse_su_with_state(self) -> None:
        # Arrange
        raw = "SU:TR=20;DS1=0;DS2=1;LS1=1;PS1=0;AS=0;AO=0;HS=1;CS=0."
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.SU
        assert msg.parameters["TR"] == "20"
        assert msg.parameters["DS1"] == "0"
        assert msg.parameters["HS"] == "1"
        assert msg.parameters["CS"] == "0"

    def test_parse_ss_with_params(self) -> None:
        # Arrange
        raw = "SS:DS1=1;LS1=0;LS2=0."
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.SS
        assert msg.parameters["DS1"] == "1"
        assert msg.parameters["LS1"] == "0"

    def test_parse_message_strips_whitespace(self) -> None:
        # Arrange
        raw = "  OK.  "
        # Act
        msg = parse_message(raw)
        # Assert
        assert msg.message_type == MessageType.OK

    def test_parse_empty_string_raises(self) -> None:
        # Arrange
        raw = ""
        # Act / Assert
        with pytest.raises(ProtocolError, match="empty"):
            parse_message(raw)

    def test_parse_missing_period_raises(self) -> None:
        # Arrange
        raw = "GS"
        # Act / Assert
        with pytest.raises(ProtocolError, match="'.'"):
            parse_message(raw)

    def test_parse_unknown_message_type_raises(self) -> None:
        # Arrange
        raw = "UNKNOWN."
        # Act / Assert
        with pytest.raises(ProtocolError, match="Unknown message type"):
            parse_message(raw)

    def test_parse_colon_with_empty_params_raises(self) -> None:
        # Arrange  — colon present but no parameters
        raw = "GS:."
        # Act / Assert
        with pytest.raises(ProtocolError):
            parse_message(raw)

    def test_parse_param_without_equals_raises(self) -> None:
        # Arrange
        raw = "HL:USRhub_user_1."
        # Act / Assert
        with pytest.raises(ProtocolError, match="'='"):
            parse_message(raw)

    def test_parse_param_with_empty_value_raises(self) -> None:
        # Arrange
        raw = "HL:USR=."
        # Act / Assert
        with pytest.raises(ProtocolError, match="Empty key or value"):
            parse_message(raw)


# ════════════════════════════════════════════════════════════════════════════
# PROTOCOL — serialize_message / builders
# ════════════════════════════════════════════════════════════════════════════

class TestSerializeMessage:

    def test_serialize_no_params(self) -> None:
        # Arrange
        msg = Message(MessageType.GS, {})
        # Act
        result = serialize_message(msg)
        # Assert
        assert result == "GS."

    def test_serialize_with_params(self) -> None:
        # Arrange
        msg = Message(MessageType.SS, {"DS1": "1", "LS1": "0"})
        # Act
        result = serialize_message(msg)
        # Assert
        assert result == "SS:DS1=1;LS1=0."

    def test_build_acc(self) -> None:
        assert build_acc() == "ACC."

    def test_build_ref(self) -> None:
        assert build_ref() == "REF."

    def test_build_ok(self) -> None:
        assert build_ok() == "OK."

    def test_build_err(self) -> None:
        assert build_err() == "ERR."

    def test_build_gs(self) -> None:
        assert build_gs() == "GS."

    def test_build_ss_single_param(self) -> None:
        result = build_ss({"AS": "1"})
        assert result == "SS:AS=1."

    def test_build_ss_multiple_params(self) -> None:
        result = build_ss({"DS1": "1", "LS1": "0", "LS2": "0"})
        assert result == "SS:DS1=1;LS1=0;LS2=0."

    def test_roundtrip_hl(self) -> None:
        # Arrange
        original = "HL:USR=hub_user_1;PWD=Password123!;HOM=home1;TT=22."
        # Act
        msg = parse_message(original)
        serialized = serialize_message(msg)
        # Assert
        assert serialized == original


# ════════════════════════════════════════════════════════════════════════════
# CREDENTIAL STORE
# ════════════════════════════════════════════════════════════════════════════

class TestInMemoryCredentialStore:

    def test_valid_credentials_accepted(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("hub_user_1", "Password123!")
        # Assert
        assert result is True

    def test_invalid_password_rejected(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("hub_user_1", "wrongpassword")
        # Assert
        assert result is False

    def test_unknown_username_rejected(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("ghost_user", "Password123!")
        # Assert
        assert result is False

    def test_empty_username_rejected(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("", "Password123!")
        # Assert
        assert result is False

    def test_empty_password_rejected(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("hub_user_1", "")
        # Assert
        assert result is False

    def test_list_credentials_returns_all_usernames(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        creds = store.list_credentials()
        # Assert
        assert "hub_user_1" in creds
        assert "hub_user_2" in creds

    def test_list_credentials_returns_copy(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        creds = store.list_credentials()
        creds["injected"] = "hacker"
        # Assert — internal store must not be mutated
        assert "injected" not in store.list_credentials()

    def test_second_user_valid_credentials(self) -> None:
        # Arrange
        store = InMemoryCredentialStore()
        # Act
        result = store.is_valid("hub_user_2", "Secure456!")
        # Assert
        assert result is True


# ════════════════════════════════════════════════════════════════════════════
# HUB SERVER — set_state validation
# ════════════════════════════════════════════════════════════════════════════

class TestHubServerSetStateValidation:

    def test_set_state_rejects_temperature_reading(self) -> None:
        # Arrange
        server = HubServer("127.0.0.1", 5000, InMemoryCredentialStore())
        hub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connected_hubs["home1"] = ConnectedHub("home1", "20", hub_socket)

        try:
            # Act
            response = server.set_state("home1", {"TR": "22"})
            # Assert
            assert response is not None
            assert response.message_type == MessageType.ERR
            assert response.parameters["REASON"] == "READ_ONLY"
            assert response.parameters["PARAMS"] == "TR"
        finally:
            hub_socket.close()

    def test_set_state_rejects_proximity_sensor(self) -> None:
        # Arrange
        server = HubServer("127.0.0.1", 5000, InMemoryCredentialStore())
        hub_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connected_hubs["home1"] = ConnectedHub("home1", "20", hub_socket)

        try:
            # Act
            response = server.set_state("home1", {"PS0": "1"})
            # Assert
            assert response is not None
            assert response.message_type == MessageType.ERR
            assert response.parameters["REASON"] == "READ_ONLY"
            assert response.parameters["PARAMS"] == "PS0"
        finally:
            hub_socket.close()
