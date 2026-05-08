from dataclasses import dataclass
from enum import Enum


class MessageType(str, Enum):
    HL = "HL"
    GS = "GS"
    SS = "SS"
    ACC = "ACC"
    REF = "REF"
    SU = "SU"
    OK = "OK"
    ERR = "ERR"


@dataclass(frozen=True)
class Message:
    message_type: MessageType
    parameters: dict[str, str]


class ProtocolError(ValueError):
    """Raised when a raw message does not conform to the CleverHub protocol."""
    pass


def parse_message(raw: str) -> Message:
    """Parse a raw protocol string into a Message.

    Format:  TYPE:KEY=VAL;KEY=VAL.   or   TYPE.
    """
    raw = raw.strip()

    if not raw:
        raise ProtocolError("Message cannot be empty")

    if not raw.endswith("."):
        raise ProtocolError("Message must end with '.'")

    content = raw[:-1]

    if ":" in content:
        type_str, param_str = content.split(":", 1)
        params = _parse_parameters(param_str)
    else:
        type_str = content
        params = {}

    try:
        msg_type = MessageType(type_str)
    except ValueError as exc:
        raise ProtocolError(f"Unknown message type: '{type_str}'") from exc

    return Message(message_type=msg_type, parameters=params)


def _parse_parameters(param_str: str) -> dict[str, str]:
    if not param_str:
        raise ProtocolError("Parameter list cannot be empty after ':'")

    params: dict[str, str] = {}
    for pair in param_str.split(";"):
        if "=" not in pair:
            raise ProtocolError(f"Invalid parameter pair (missing '='): '{pair}'")
        key, value = pair.split("=", 1)
        if not key or not value:
            raise ProtocolError(f"Empty key or value in pair: '{pair}'")
        params[key] = value
    return params


def serialize_message(message: Message) -> str:
    if not message.parameters:
        return f"{message.message_type.value}."
    param_str = ";".join(f"{k}={v}" for k, v in message.parameters.items())
    return f"{message.message_type.value}:{param_str}."


# ── convenience builders ────────────────────────────────────────────────────

def build_acc() -> str:
    return serialize_message(Message(MessageType.ACC, {}))


def build_ref() -> str:
    return serialize_message(Message(MessageType.REF, {}))


def build_gs() -> str:
    return serialize_message(Message(MessageType.GS, {}))


def build_ss(parameters: dict[str, str]) -> str:
    return serialize_message(Message(MessageType.SS, parameters))


def build_ok() -> str:
    return serialize_message(Message(MessageType.OK, {}))


def build_err() -> str:
    return serialize_message(Message(MessageType.ERR, {}))
