import pytest
from cleverhome.protocolo import (
    parse_message,
    MessageType,
    ProtocolError,
    build_acc_message,
    build_ref_message,
    build_gs_message,
    build_ss_message,
    serialize_message,
    Message,
)

# 1. Parse HL message
def test_parse_hl_message() -> None:
    # Arrange
    raw = "HL:USR=hub_user_1;PWD=Password123!;HOM=home1;TT=20."
    # Act
    message = parse_message(raw)
    # Assert
    assert message.message_type == MessageType.HL
    assert message.parameters["USR"] == "hub_user_1"
    assert message.parameters["PWD"] == "Password123!"
    assert message.parameters["HOM"] == "home1"
    assert message.parameters["TT"] == "20"

# 2. Parse GS message (no parameters)
def test_parse_gs_message() -> None:
    # Arrange
    raw = "GS."
    # Act
    message = parse_message(raw)
    # Assert
    assert message.message_type == MessageType.GS
    assert message.parameters == {}

# 3. Parse SU message
def test_parse_su_message() -> None:
    # Arrange
    raw = "SU:TR=20;DS1=0;LS1=1;AS=0;AO=0;HS=1;CS=0."
    # Act
    message = parse_message(raw)
    # Assert
    assert message.message_type == MessageType.SU
    assert message.parameters["TR"] == "20"
    assert message.parameters["DS1"] == "0"
    assert message.parameters["LS1"] == "1"

# 4. Parse SS message
def test_parse_ss_message() -> None:
    # Arrange
    raw = "SS:DS1=1;LS1=0;LS2=0."
    # Act
    message = parse_message(raw)
    # Assert
    assert message.message_type == MessageType.SS
    assert message.parameters["DS1"] == "1"
    assert message.parameters["LS1"] == "0"

# 5. Message must end with period
def test_parse_message_without_period() -> None:
    # Arrange
    raw = "GS"
    # Act & Assert
    with pytest.raises(ProtocolError):
        parse_message(raw)

# 6. Empty message raises error
def test_parse_empty_message() -> None:
    # Arrange
    raw = ""
    # Act & Assert
    with pytest.raises(ProtocolError):
        parse_message(raw)

# 7. Unknown message type raises error
def test_parse_unknown_message_type() -> None:
    # Arrange
    raw = "UNKNOWN."
    # Act & Assert
    with pytest.raises(ProtocolError):
        parse_message(raw)

# 8. Invalid parameter format raises error
def test_parse_invalid_parameter_format() -> None:
    # Arrange
    raw = "HL:USR."
    # Act & Assert
    with pytest.raises(ProtocolError):
        parse_message(raw)

# 9. Build ACC message
def test_build_acc_message() -> None:
    # Arrange & Act
    result = build_acc_message()
    # Assert
    assert result == "ACC."

# 10. Build REF message
def test_build_ref_message() -> None:
    # Arrange & Act
    result = build_ref_message()
    # Assert
    assert result == "REF."

# 11. Build GS message
def test_build_gs_message() -> None:
    # Arrange & Act
    result = build_gs_message()
    # Assert
    assert result == "GS."

# 12. Build SS message
def test_build_ss_message() -> None:
    # Arrange
    parameters = {"DS1": "1", "LS1": "0"}
    # Act
    result = build_ss_message(parameters)
    # Assert
    assert result == "SS:DS1=1;LS1=0."