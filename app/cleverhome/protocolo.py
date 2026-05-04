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
    pass


def parse_message(raw_message: str) -> Message:
    raw_message = raw_message.strip()

    if not raw_message:
        raise ProtocolError("Message cannot be empty")

    if not raw_message.endswith("."):
        raise ProtocolError("Message must end with '.'")

    content = raw_message[:-1]

    if ":" in content:
        message_type_text, parameter_text = content.split(":", 1)
        parameters = parse_parameters(parameter_text)
    else:
        message_type_text = content
        parameters = {}

    try:
        message_type = MessageType(message_type_text)
    except ValueError as exc:
        raise ProtocolError(f"Unknown message type: {message_type_text}") from exc

    return Message(message_type=message_type, parameters=parameters)


def parse_parameters(parameter_text: str) -> dict[str, str]:
    if not parameter_text:
        raise ProtocolError("Parameter list cannot be empty")

    parameters: dict[str, str] = {}

    pairs = parameter_text.split(";")

    for pair in pairs:
        if "=" not in pair:
            raise ProtocolError(f"Invalid parameter format: {pair}")

        key, value = pair.split("=", 1)

        if not key or not value:
            raise ProtocolError(f"Invalid parameter key/value: {pair}")

        parameters[key] = value

    return parameters


def serialize_message(message: Message) -> str:
    if not message.parameters:
        return f"{message.message_type.value}."

    parameter_text = ";".join(
        f"{key}={value}" for key, value in message.parameters.items()
    )

    return f"{message.message_type.value}:{parameter_text}."


def build_acc_message() -> str:
    return serialize_message(Message(MessageType.ACC, {}))


def build_ref_message() -> str:
    return serialize_message(Message(MessageType.REF, {}))


def build_gs_message() -> str:
    return serialize_message(Message(MessageType.GS, {}))


def build_ss_message(parameters: dict[str, str]) -> str:
    return serialize_message(Message(MessageType.SS, parameters))


def build_ok_message() -> str:
    return serialize_message(Message(MessageType.OK, {}))


def build_err_message() -> str:
    return serialize_message(Message(MessageType.ERR, {}))