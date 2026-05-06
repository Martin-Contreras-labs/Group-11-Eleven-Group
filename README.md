# Group-11-Eleven-Group
Software Design Repository Group 11

Members : Martin Contreras - Matias de la Sota - Benjamin Duran

For this first iteration, the implemented functionalities are:

 --------> Main Functionalities Included in This Submission <--------

1. CleverHub protocol handling:
   - Parse incoming protocol messages.
   - Serialize outgoing protocol messages.
   - Support the following message types: HL, GS, SS, ACC, REF, SU, OK, and ERR.

2. CleverHub authentication:
   - Store predefined CleverHub credentials in memory.
   - Validate the username and password received in the HL message.
   - Accept valid CleverHubs using ACC.
   - Reject invalid CleverHubs using REF.

3. TCP CleverHub server:
   - Listen for CleverHub connections.
   - Accept a CleverHub connection after a valid HL message.
   - Store connected homes by home name.
   - Allow the platform to request the status of a connected home.
   - Allow the platform to send state changes to a connected home.

4. Console-based UI:
   - List connected homes.
   - Request the status of a selected home.
   - Set device states using protocol parameters.
   - List stored CleverHub credentials.
   - Exit the platform safely.

5. Static type checking:
   - Python type hints were added to the implemented modules.
   - mypy was configured and executed successfully.


-------> How works de main files in cleverhome <-----------

- protocolo.py :

This module contains the implementation of the CleverHub text-based protocol. It is responsible for parsing raw messages received from CleverHubs and serializing platform messages before sending them. The protocol module helps keep message parsing and message creation separated from the TCP server and the console interface.

- credenciales.py :

This module implements a simple in-memory credential store. For this submission, predefined CleverHub credentials are stored using a Python dictionary.
This satisfies the requirement of having a simple non-database credential store for the first iteration.

- server_hub.py :

This module implements the TCP server used by the CleverHome Platform to communicate with CleverHubs.

Its responsibilities are:

Open a TCP socket.
Listen for CleverHub connections.
Receive the first HL message from a CleverHub.
Validate the received credentials.
Respond with ACC. if the CleverHub is accepted.
Respond with REF. if the CleverHub is rejected.
Store accepted CleverHub connections.
Send GS. requests to connected CleverHubs.
Send SS:... commands to update device states.
The server also supports a safe shutdown when the user exits the console UI.


- consola_simple.py :

This module implements the console-based user interface.
The current menu is:

====== CleverHome Platform Console ======
1. List connected homes
2. Request house status
3. Set device state
4. List stored credentials
5. Exit

Through this interface, the user can interact with connected CleverHubs and send protocol commands without manually writing socket code.


 -----> How run the menu <------------------

$env:PYTHONPATH="app"
python -m cleverhome.console_ui


# We use manual local testings for the menu and the connection with the server, for that the folder manual_files is, and the files there.

