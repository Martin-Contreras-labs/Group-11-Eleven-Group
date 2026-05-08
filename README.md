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

# C4 System Context Diagram
The system context diagram defines the CleverHome Platform as the central software system, identifying the two actors that interact with it.
CleverHome Platform is the software system being built. It is responsible for connecting users to their smart homes by communicating with CleverHubs installed in each house.
User is a person who interacts with the platform through a console interface. They send requests to monitor sensor data and control smart devices, and receive information about the current state of their home in return.
CleverHub is an external software system — a hardware device installed in each home that acts as an intermediary between the platform and the smart devices inside the house. Communication with the platform is bidirectional: the CleverHub initiates the connection using the HL message and sends state updates and responses (SU, OK, ERR), while the platform sends commands to request or modify state (GS, SS).
The context diagram deliberately excludes internal architecture and technology details, focusing only on who uses the system and what external systems it depends on, following the C4 model's intent for this level.

# C4 Containers Diagram
The containers diagram shows the internal structure of the CleverHome Platform for this first iteration. Only containers that are actually implemented in this submission are included.
Console Application is a Python CLI application that serves as the user-facing interface. It allows users to list credentials, view sensor states, and send device commands. It communicates with the Backend Application through direct function calls, passing user requests and displaying the results returned.
Backend Application is a Python server application that centralises all business logic for this iteration. It is responsible for:

Accepting and managing TCP connections from CleverHubs
Implementing the CleverHub communication protocol (HL, GS, SS)
Validating hub credentials using an in-memory credential store
Maintaining the current state of each connected home

The Backend sends commands to the CleverHub over TCP (GS to request state, SS to change device state), and receives protocol messages back (HL for connection initialization, SU for state updates, OK/ERR for command acknowledgments).
The decision to separate the Console Application from the Backend Application follows the separation of concerns principle: user interaction is isolated from protocol handling and business logic. This also makes it easier to replace the console interface with a web-based UI in future iterations without touching the backend.
Docker is used to deploy each application in its own container, but is not represented in the C4 diagram since it is a deployment concern rather than a logical architectural one.

# UML Sequence Diagrams
Three sequence diagrams document the complete CleverHub communication protocol.
## Diagram 1 — Hub Connection (HL): 
The CleverHub initiates all connections by sending an HL message containing credentials (USR, PWD), the home identifier (HOM), and the target temperature (TT). The Backend Application validates the credentials against the Credential Store and checks for duplicate connections. If valid, it responds with ACC (accepted); otherwise with REF (refused). This is the only message initiated by the CleverHub.
## Diagram 2 — Get State (GS / SU): 
Triggered by the user via the Console Application, the platform sends a GS message (no parameters) to the relevant CleverHub. The hub responds with an SU message containing the current values of all state parameters: temperature reading (TR), door states (DS), light states (LS), proximity sensors (PS), alarm state (AS), alarm sounding (AO), heater (HS), and chiller (CS). The backend parses and stores this state before returning it to the console for display.
## Diagram 3 — Set State (SS / OK / ERR): 
The user issues a device command through the console. The backend constructs and sends an SS message with the parameters to modify (e.g., SS:DS1=1;LS1=0;LS2=0.). The CleverHub responds with OK if the state was successfully applied, or ERR if it failed. The outcome is returned to the console and displayed to the user. The paramaters used to set state are: door states (DS), light states (LS), alarm state (AS), alarm sounding (AO), heater (HS), and chiller (CS). Note that read-only parameters temperature reading and proximity sensors (TR, PS) cannot be set via SS.


# How works the main files in cleverhome

## protocolo.py:

This module contains the implementation of the CleverHub text-based protocol. It is responsible for parsing raw messages received from CleverHubs and serializing platform messages before sending them. The protocol module helps keep message parsing and message creation separated from the TCP server and the console interface.

## credenciales.py:

This module implements a simple in-memory credential store. For this submission, predefined CleverHub credentials are stored using a Python dictionary.
This satisfies the requirement of having a simple non-database credential store for the first iteration.

## server_hub.py:

This module implements the TCP server used by the CleverHome Platform to communicate with CleverHubs.

### Its responsibilities are:

- Open a TCP socket.
- Listen for CleverHub connections.
- Receive the first HL message from a CleverHub.
- Validate the received credentials.
- Respond with ACC if the CleverHub is accepted.
- Respond with REF if the CleverHub is rejected.
- Store accepted CleverHub connections.
- Send GS. requests to connected CleverHubs.
- Send SS:... commands to update device states.
The server also supports a safe shutdown when the user exits the console UI.


## consola_simple.py:

This module implements the console-based user interface.
The current menu is:

====== CleverHome Platform Console ======
1. List connected homes
2. Request house status
3. Set device state
4. List stored credentials
5. Exit

Through this interface, the user can interact with connected CleverHubs and send protocol commands without manually writing socket code.


# How run the menu:
To run the console menu, execute the following command in the terminal:

```powershell
$env:PYTHONPATH="app"
python -m cleverhome.console_ui
```

# Manual Testing
We use manual local testings for the menu and the connection with the server, for that the folder manual_files is, and the files there.

