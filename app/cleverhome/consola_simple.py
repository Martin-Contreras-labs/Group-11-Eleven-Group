import threading

from cleverhome.credenciales import CredentialStore
from cleverhome.server_hub import HubServer
from cleverhome.protocolo import MessageType


def main() -> None:
    credential_store = CredentialStore()
    hub_server = HubServer(
        host="0.0.0.0",
        port=5000,
        credential_store=credential_store,
    )

    server_thread = threading.Thread(
    target=hub_server.start,
    daemon=False,
    )
    server_thread.start()

    run_console_menu(hub_server, credential_store)
    server_thread.join(timeout=2)


def run_console_menu(
    hub_server: HubServer,
    credential_store: CredentialStore,
) -> None:
    while True:
        print("")
        print("====== CleverHome Platform Console ======")
        print("1. List connected homes")
        print("2. Request house status")
        print("3. Set device state")
        print("4. List stored credentials")
        print("5. Exit")
        print("========================================")

        option = input("Choose an option: ").strip()

        if option == "1":
            list_connected_homes(hub_server)

        elif option == "2":
            request_house_status(hub_server)

        elif option == "3":
            set_device_state(hub_server)

        elif option == "4":
            list_credentials(credential_store)

        elif option == "5":
            print("Stopping CleverHome Platform...")
            hub_server.stop()
            break

        else:
            print("Invalid option. Please choose a valid option.")


def list_connected_homes(hub_server: HubServer) -> None:
    homes = hub_server.list_connected_homes()

    if not homes:
        print("No homes connected.")
        return

    print("Connected homes:")

    for home in homes:
        print(f"- {home}")


def request_house_status(hub_server: HubServer) -> None:
    home_name = input("Enter home name: ").strip()

    response = hub_server.request_status(home_name)

    if response is None:
        print("Could not get status. Check if the home is connected.")
        return

    if response.message_type != MessageType.SU:
        print(f"Unexpected response: {response.message_type.value}")
        return

    print("House status:")

    for key, value in response.parameters.items():
        print(f"- {key}: {value}")


def set_device_state(hub_server: HubServer) -> None:
    home_name = input("Enter home name: ").strip()

    print("Enter the state changes using the protocol parameter format.")
    print("Example: DS1=1;LS1=0;AS=1")

    raw_parameters = input("State changes: ").strip()

    parameters = parse_console_parameters(raw_parameters)

    if parameters is None:
        print("Invalid parameter format.")
        return

    response = hub_server.set_state(home_name, parameters)

    if response is None:
        print("Could not set state. Check if the home is connected.")
        return

    if response.message_type == MessageType.OK:
        print("State changed successfully.")
    elif response.message_type == MessageType.ERR:
        print("The CleverHub returned an error.")
    else:
        print(f"Unexpected response: {response.message_type.value}")


def parse_console_parameters(raw_parameters: str) -> dict[str, str] | None:
    if not raw_parameters:
        return None

    parameters: dict[str, str] = {}

    pairs = raw_parameters.split(";")

    for pair in pairs:
        if "=" not in pair:
            return None

        key, value = pair.split("=", 1)

        if not key or not value:
            return None

        parameters[key] = value

    return parameters


def list_credentials(credential_store: CredentialStore) -> None:
    credentials = credential_store.list_credentials()

    print("Stored CleverHub credentials:")

    for username in credentials:
        print(f"- {username}")


if __name__ == "__main__":
    main()