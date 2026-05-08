import threading

from cleverhome.credential_store import AbstractCredentialStore, InMemoryCredentialStore
from cleverhome.hub_server import AbstractHubServer, HubServer
from cleverhome.protocol import MessageType


def main() -> None:
    credential_store: AbstractCredentialStore = InMemoryCredentialStore()
    hub_server: AbstractHubServer = HubServer(
        host="0.0.0.0",
        port=5000,
        credential_store=credential_store,
    )

    server_thread = threading.Thread(target=hub_server.start, daemon=True)
    server_thread.start()

    run_console(hub_server, credential_store)
    hub_server.stop()
    server_thread.join(timeout=2)


def run_console(
    hub_server: AbstractHubServer,
    credential_store: AbstractCredentialStore,
) -> None:
    while True:
        print("\n====== CleverHome Platform Console ======")
        print("1. List connected homes")
        print("2. Request house status")
        print("3. Set device state")
        print("4. List stored credentials")
        print("5. Exit")
        print("=========================================")

        option = input("Choose an option: ").strip()

        if option == "1":
            _list_homes(hub_server)
        elif option == "2":
            _request_status(hub_server)
        elif option == "3":
            _set_state(hub_server)
        elif option == "4":
            _list_credentials(credential_store)
        elif option == "5":
            print("Stopping CleverHome Platform…")
            break
        else:
            print("Invalid option. Please choose between 1 and 5.")


# ── menu handlers ────────────────────────────────────────────────────────────

def _list_homes(hub_server: AbstractHubServer) -> None:
    homes = hub_server.list_connected_homes()
    if not homes:
        print("No homes connected.")
        return
    print("Connected homes:")
    for home in homes:
        print(f"  - {home}")


def _request_status(hub_server: AbstractHubServer) -> None:
    home_name = input("Enter home name: ").strip()
    response = hub_server.request_status(home_name)

    if response is None:
        print("Could not get status. Is the home connected?")
        return

    if response.message_type != MessageType.SU:
        print(f"Unexpected response: {response.message_type.value}")
        return

    print("House status:")
    for key, value in response.parameters.items():
        print(f"  {key}: {value}")


def _set_state(hub_server: AbstractHubServer) -> None:
    home_name = input("Enter home name: ").strip()
    if home_name not in hub_server.list_connected_homes():
        print("Could not set state. Is the home connected?")
        return

    print("Enter state changes (e.g. DS1=1;LS1=0;AS=1):")
    raw = input("State changes: ").strip()

    params = _parse_params(raw)
    if params is None:
        print("Invalid parameter format.")
        return

    response = hub_server.set_state(home_name, params)
    if response is None:
        print("Could not set state. Is the home connected?")
        return

    if response.message_type == MessageType.OK:
        print("State changed successfully.")
    elif response.message_type == MessageType.ERR:
        if response.parameters.get("REASON") == "READ_ONLY":
            print(
                "Invalid state change. Read-only parameters cannot be set: "
                + response.parameters.get("PARAMS", "")
            )
        else:
            print("The CleverHub returned an error.")
    else:
        print(f"Unexpected response: {response.message_type.value}")


def _list_credentials(credential_store: AbstractCredentialStore) -> None:
    creds = credential_store.list_credentials()
    print("Stored CleverHub credentials (usernames only):")
    for username in creds:
        print(f"  - {username}")


def _parse_params(raw: str) -> dict[str, str] | None:
    if not raw:
        return None
    params: dict[str, str] = {}
    for pair in raw.split(";"):
        if "=" not in pair:
            return None
        key, value = pair.split("=", 1)
        if not key or not value:
            return None
        params[key] = value
    return params


if __name__ == "__main__":
    main()
