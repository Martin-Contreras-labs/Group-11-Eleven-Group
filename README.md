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
