import socket
import threading

from cleverhome.credenciales import CredentialStore
from cleverhome.protocolo import (
    Message,
    MessageType,
    ProtocolError,
    build_acc_message,
    build_ref_message,
    build_gs_message,
    build_ss_message,
    parse_message,
)


class ConnectedHub:
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


class HubServer:
    def __init__(
        self,
        host: str,
        port: int,
        credential_store: CredentialStore,
    ) -> None:
        self.host = host
        self.port = port
        self.credential_store = credential_store
        self.connected_hubs: dict[str, ConnectedHub] = {}
        self._server_socket: socket.socket | None = None
        self._running = False

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen()

        self._running = True

        print(f"CleverHome Platform listening on {self.host}:{self.port}")

        while self._running:
            try:
                connection, address = self._server_socket.accept()
            except OSError:
                break

            print(f"New connection from {address}")

            client_thread = threading.Thread(
                target=self._handle_connection,
                args=(connection,),
                daemon=True,
            )
            client_thread.start()

    def stop(self) -> None:
        self._running = False

        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass

    def _handle_connection(self, connection: socket.socket) -> None:
        try:
            raw_message = self._receive_message(connection)
            message = parse_message(raw_message)

            if message.message_type != MessageType.HL:
                connection.sendall(build_ref_message().encode())
                connection.close()
                return

            username = message.parameters.get("USR", "")
            password = message.parameters.get("PWD", "")
            home_name = message.parameters.get("HOM", "")
            target_temperature = message.parameters.get("TT", "")

            if not username or not password or not home_name:
                connection.sendall(build_ref_message().encode())
                connection.close()
                return

            if home_name in self.connected_hubs:
                connection.sendall(build_ref_message().encode())
                connection.close()
                return

            if not self.credential_store.is_valid(username, password):
                connection.sendall(build_ref_message().encode())
                connection.close()
                return

            self.connected_hubs[home_name] = ConnectedHub(
                home_name=home_name,
                target_temperature=target_temperature,
                connection=connection,
            )

            connection.sendall(build_acc_message().encode())
            print(f"Hub accepted for home: {home_name}")

        except (ProtocolError, OSError) as error:
            print(f"Connection error: {error}")
            connection.close()

    def _receive_message(self, connection: socket.socket) -> str:
        data = connection.recv(1024)

        if not data:
            raise ProtocolError("Empty message received from hub")

        return data.decode().strip()

    def list_connected_homes(self) -> list[str]:
        return list(self.connected_hubs.keys())

    def request_status(self, home_name: str) -> Message | None:
        hub = self.connected_hubs.get(home_name)

        if hub is None:
            return None

        try:
            hub.connection.sendall(build_gs_message().encode())

            raw_response = self._receive_message(hub.connection)
            response = parse_message(raw_response)

            if response.message_type == MessageType.SU:
                hub.last_status = response
                return response

            return response

        except (ProtocolError, OSError) as error:
            print(f"Could not request status from {home_name}: {error}")
            return None

    def set_state(self, home_name: str, parameters: dict[str, str]) -> Message | None:
        hub = self.connected_hubs.get(home_name)

        if hub is None:
            return None

        try:
            command = build_ss_message(parameters)
            hub.connection.sendall(command.encode())

            raw_response = self._receive_message(hub.connection)
            response = parse_message(raw_response)

            return response

        except (ProtocolError, OSError) as error:
            print(f"Could not set state for {home_name}: {error}")
            return None