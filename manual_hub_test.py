import socket

HOST = "127.0.0.1"
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    hello_message = "HL:USR=hub_user_1;PWD=Password123!;HOM=home1;TT=20."
    client.sendall(hello_message.encode())

    response = client.recv(1024).decode()
    print("Response from platform:", response)

    if response != "ACC.":
        print("Connection refused by platform.")
        raise SystemExit

    print("Manual hub connected as home1.")
    print("Waiting for GS or SS commands from the platform...")

    while True:
        command = client.recv(1024).decode().strip()

        if not command:
            print("Platform closed the connection.")
            break

        print("Command received from platform:", command)

        if command == "GS.":
            status = "SU:TR=20;DS1=0;DS2=1;LS1=1;PS1=0;AS=0;AO=0;HS=1;CS=0."
            client.sendall(status.encode())

        elif command.startswith("SS:"):
            client.sendall("OK.".encode())

        else:
            client.sendall("ERR.".encode())