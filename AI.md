# AI Usage

This document describes how and where AI assistants (ChatGPT and Claude) were used during this submission. All AI-generated content was reviewed, validated, and adapted by the team before being included.

---

## Part 1 — Design

AI assistance (Claude) was used for the following:

- Generating and iterating on the C4 Context and Container diagrams, including reviewing adherence to C4 model rules as taught in class.
- Reviewing and correcting arrow directionality and relationship descriptions in both diagrams, replacing ambiguous bidirectional arrows with explicit directional relationships.
- Generating UML Sequence Diagram visuals and verifying complete coverage of all protocol messages (`HL`, `GS`, `SS`, `ACC`, `REF`, `SU`, `OK`, `ERR`).
- Drafting the design documentation text for the README, including justifications for architectural decisions (separation of concerns, dependency inversion, thread-per-hub scalability).

All design decisions were validated and adapted by the team. The final diagrams were created by the team in draw.io based on the reviewed designs.

---

## Part 2 — Implementation

AI assistance (ChatGPT and Claude) was used as a support tool throughout the development process.

### Initial structure and architecture (ChatGPT)

- Understanding and summarizing the project requirements.
- Proposing an initial Python project structure with separate modules for protocol handling, credential storage, TCP communication, and console interaction.
- Explaining and configuring `mypy` for static type checking.

### Protocol validation and CleverHub compatibility (ChatGPT)

- Identifying and fixing protocol parsing issues that prevented the platform from connecting correctly to the professor's CleverHub simulator.
- Correcting the exact message format and parameter structure so that `HL`, `GS`, and `SS` messages were accepted by the real simulator.
- Debugging specific commands and responses to ensure the platform could complete a full connection handshake and exchange state messages successfully.

### Refactoring and SOLID principles (Claude)

- Refactoring the codebase to introduce abstract interfaces (`AbstractCredentialStore`, `AbstractHubServer`), applying the Dependency Inversion Principle so that the server and console depend on abstractions rather than concrete classes.
- Ensuring the Single Responsibility Principle was applied by keeping protocol parsing, credential validation, TCP communication, and UI interaction in separate modules.
- Reviewing the overall structure for adherence to SOLID principles and suggesting improvements.

### Console UI and Docker setup (Claude)

- Generating corrected Docker and docker-compose configuration to support the interactive console UI (`stdin_open: true`, `tty: true`).
- Providing the specific Docker commands needed to connect the CleverHub simulator to the running platform container.
- Writing the GitHub Actions CI workflow (`ci.yml`) with three independent jobs (pytest, mypy, docker build) each capped at `timeout-minutes: 5` as required.

### Testing (Claude)

- Generating a comprehensive set of unit tests (30+) covering valid and invalid protocol messages, credential store behaviour, and mutation safety, all following the Arrange / Act / Assert structure.

### Documentation (Claude)

- Writing and updating the `README.md` to meet all submission requirements, including the code structure explanation, test justification table, how-to-run instructions, and what-was-not-completed section.

---

All code and documentation generated with AI assistance was reviewed and tested by the team before being included in the submission.