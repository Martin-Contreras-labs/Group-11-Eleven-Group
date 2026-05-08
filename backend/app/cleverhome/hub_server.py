import socket
import threading
from abc import ABC, abstractmethod

from cleverhome.credential_store import AbstractCredentialStore
from cleverhome.protocol import (
    Message,
    MessageType,
    ProtocolError,
    build_acc,
    build_ref,
    build_gs,
    build_ss,
    parse_message,
)


class ConnectedHub:
    """Represents a CleverHub that has successfully authenticated."""

    def __init__(
        self,
        home_name: str,
        target_temperature: str,
        connection: socket.socket,
    ) -> None:
        self.home_name = home_name
        self.target_temperature = target_temperature
        self.connection = connection
        self.last_status: Message | None = None


class AbstractHubServer(ABC):
    """Interface for the CleverHub TCP server.

    Keeping the interface separate from the implementation allows tests to
    inject fakes and makes it easy to swap the transport layer later
    (e.g., WebSockets) without changing the console or business logic.
    """

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def list_connected_homes(self) -> list[str]: ...

    @abstractmethod
    def request_status(self, home_name: str) -> Message | None: ...

    @abstractmethod
    def set_state(self, home_name: str, parameters: dict[str, str]) -> Message | None: ...


class HubServer(AbstractHubServer):
    """TCP server that implements the CleverHub communication protocol.

    Each CleverHub connection is handled in its own daemon thread, so the
    server can serve hundreds of concurrent hubs (scalability QA scenario).
    The credential store is injected via the constructor (DIP), so it can be
    swapped for a database-backed store in a future iteration.
    """

    def __init__(
        self,
        host: str,
        port: int,
        credential_store: AbstractCredentialStore,
    ) -> None:
        self.host = host
        self.port = port
        self._credential_store = credential_store
        self.connected_hubs: dict[str, ConnectedHub] = {}
        self._server_socket: socket.socket | None = None
        self._running = False

    # ── lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()
        self._running = True
        print(f"[Server] Listening on {self.host}:{self.port}")

        while self._running:
            try:
                conn, addr = self._server_socket.accept()
            except OSError:
                break
            if not self._running:
                conn.close()
                break
            print(f"[Server] New connection from {addr}")
            threading.Thread(
                target=self._handle_connection,
                args=(conn,),
                daemon=True,
            ).start()

    def stop(self) -> None:
        self._running = False
        self._wake_accept()
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass

    # ── public API ───────────────────────────────────────────────────────────

    def list_connected_homes(self) -> list[str]:
        return list(self.connected_hubs.keys())

    def request_status(self, home_name: str) -> Message | None:
        hub = self.connected_hubs.get(home_name)
        if hub is None:
            return None
        try:
            hub.connection.sendall(build_gs().encode())
            raw = self._recv(hub.connection)
            response = parse_message(raw)
            if response.message_type == MessageType.SU:
                hub.last_status = response
            return response
        except (ProtocolError, OSError) as err:
            print(f"[Server] Error requesting status from '{home_name}': {err}")
            return None

    def set_state(self, home_name: str, parameters: dict[str, str]) -> Message | None:
        hub = self.connected_hubs.get(home_name)
        if hub is None:
            return None
        read_only = self._read_only_parameters(parameters)
        if read_only:
            print(
                "[Server] Refusing read-only state parameters: "
                + ", ".join(read_only)
            )
            return Message(
                MessageType.ERR,
                {"REASON": "READ_ONLY", "PARAMS": ",".join(read_only)},
            )
        try:
            hub.connection.sendall(build_ss(parameters).encode())
            raw = self._recv(hub.connection)
            return parse_message(raw)
        except (ProtocolError, OSError) as err:
            print(f"[Server] Error setting state for '{home_name}': {err}")
            return None

    # ── private helpers ──────────────────────────────────────────────────────

    def _handle_connection(self, connection: socket.socket) -> None:
        try:
            raw = self._recv(connection)
            message = parse_message(raw)

            if message.message_type != MessageType.HL:
                connection.sendall(build_ref().encode())
                connection.close()
                return

            usr = message.parameters.get("USR", "")
            pwd = message.parameters.get("PWD", "")
            home = message.parameters.get("HOM", "")
            tt = message.parameters.get("TT", "")

            if not usr or not pwd or not home:
                connection.sendall(build_ref().encode())
                connection.close()
                return

            if home in self.connected_hubs:
                connection.sendall(build_ref().encode())
                connection.close()
                return

            if not self._credential_store.is_valid(usr, pwd):
                connection.sendall(build_ref().encode())
                connection.close()
                return

            self.connected_hubs[home] = ConnectedHub(
                home_name=home,
                target_temperature=tt,
                connection=connection,
            )
            connection.sendall(build_acc().encode())
            print(f"[Server] Hub accepted for home: '{home}'")

        except (ProtocolError, OSError) as err:
            print(f"[Server] Connection error: {err}")
            connection.close()

    def _recv(self, connection: socket.socket) -> str:
        data = connection.recv(4096)
        if not data:
            raise ProtocolError("Connection closed before receiving a message")
        return data.decode().strip()

    def _wake_accept(self) -> None:
        if self._server_socket is None:
            return
        host = "127.0.0.1" if self.host == "0.0.0.0" else self.host
        try:
            with socket.create_connection((host, self.port), timeout=0.2):
                pass
        except OSError:
            pass

    def _read_only_parameters(self, parameters: dict[str, str]) -> list[str]:
        read_only: list[str] = []
        for key in parameters:
            normalized = key.upper()
            if normalized == "TR" or (
                normalized.startswith("PS") and normalized[2:].isdigit()
            ):
                read_only.append(key)
        return read_only
