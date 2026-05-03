## Main Functionalities

1. **CleverHub Connection**: The platform accepts incoming connections from CleverHubs using the defined TCP/IP text-based protocol, including credential validation.

2. **Get House Status**: The platform can request the current state of all sensors and devices in a connected house via the GS command.

3. **Set Device State**: The platform can send commands to change the state of devices in a connected house via the SS command.

4. **Credential Store**: The platform maintains a predefined list of valid CleverHub credentials, used to accept or reject incoming connections.

5. **Console UI**: A console-based interface that allows a user to view the status of sensors and set the state of devices in a connected house.

6. **List Credentials**: The Console UI allows listing all stored CleverHub credentials.

## Quality Attribute Scenarios

### Scenario 1: Security

**Justification**: The platform allows users to remotely access and control their homes through the Internet. The platform must ensure that house data is private and only accessible to authorized users. A security breach could allow unauthorized actors to control devices in someone's home.

|                                  |                                                                                        |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| **Category / Quality Attribute** | Security                                                                               |
| **Description**                  | An unauthorized actor attempts to connect to the platform using invalid credentials    |
| **1. Stimulus Source**           | Unauthorized external actor                                                            |
| **2. Stimulus**                  | Connection attempt using invalid or stolen CleverHub credentials                       |
| **3. Environment**               | Platform running normally, accepting incoming CleverHub connections                    |
| **4. Artifact**                  | CleverHub connection handler and credential store                                      |
| **5. Response**                  | The platform rejects the connection and sends a REF response. No house data is exposed |
| **6. Response Measure**          | 100% of connection attempts with invalid credentials are rejected within 500ms         |
| **Priority**                     | High                                                                                   |
| **Difficulty**                   | Medium                                                                                 |

---

### Scenario 2: Scalability

**Justification**: The platform is expected to serve millions of customers and hundreds of CleverHubs simultaneously. The platform must handle multiple smart homes without performance hits to allow the business to grow and add more houses to their customer base.

|                                  |                                                                                                                    |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Category / Quality Attribute** | Scalability                                                                                                        |
| **Description**                  | Multiple CleverHubs send requests simultaneously and the platform handles them all without performance degradation |
| **1. Stimulus Source**           | Multiple CleverHubs connecting simultaneously                                                                      |
| **2. Stimulus**                  | 100 CleverHubs send a GS request at the same time                                                                  |
| **3. Environment**               | Platform running under normal operating conditions                                                                 |
| **4. Artifact**                  | CleverHub connection handler                                                                                       |
| **5. Response**                  | The platform handles all requests concurrently without dropping connections or degrading response time             |
| **6. Response Measure**          | All 100 requests are processed and responded to within 2 seconds                                                   |
| **Priority**                     | High                                                                                                               |
| **Difficulty**                   | High                                                                                                               |
                                                                                                           |

## Domain Model

```mermaid

---
classDiagram
    class User {
        username
        password
    }

    class House {
        houseName
        targetTemperature
        lastOccupancyDetected
        vacancyThresholdMinutes
    }

    class CleverHub {
        hubName
    }

    class SmartDevice {
        deviceName
    }

    class Sensor {
        sensorType
        currentValue
    }

    class Actuator {
        actuatorType
        currentState
    }

    class SmartLightBulb {
        isOn
    }

    class TemperatureSensor {
        temperature
    }

    class DoorLock {
        doorNumber
        isLocked
    }

    class ProximitySensor {
        sensorNumber
        movementDetected
    }

    class AlarmSystem {
        isEnabled
        isSounding
    }

    class HvacSystem {
    currentState
    }
    class Heater {
        isActive
    }

    class Chiller {
        isActive
    }

    class SensorLog {
        sensorValue
        timestamp
    }

    class ActionLog {
        actionPerformed
        timestamp
    }

    User "1" -- "0..*" House : owns
    House "1" -- "1" CleverHub : has
    CleverHub "1" -- "0..*" SmartDevice : manages
    SmartDevice "1" -- "0..*" Sensor : is
    SmartDevice "1" -- "0..*" Actuator : is
    SmartDevice "1" -- "1" TemperatureSensor : is
    SmartDevice "1" -- "1" HvacSystem : is
    Sensor "1" -- "0..*" ProximitySensor : is
    Actuator "1" -- "0..*" SmartLightBulb : is
    Actuator "1" -- "0..*" DoorLock : is
    Actuator "1" -- "1" AlarmSystem : is
    HvacSystem "1" -- "1" Heater : contains
    HvacSystem "1" -- "1" Chiller : contains
    House "1" -- "0..*" SensorLog : records
    House "1" -- "0..*" ActionLog : records
    Sensor "1" -- "0..*" SensorLog : generates
    Actuator "1" -- "0..*" ActionLog : logs
```

### Relationships

- **CleverHub manages SmartDevice**: The platform never communicates directly with individual smart devices. All communication goes through the CleverHub, which acts as intermediary between the platform and the devices in a house.

### Domain Rules

1. If a door is manually unlocked while the alarm is enabled, or movement is detected while the alarm is enabled → the alarm starts sounding.
2. If a house has been vacant for more than `vacancyThresholdMinutes` without movement detected → lock all doors, turn off all lights, enable alarm.
3. If enough movement is detected → turn on lights automatically.
4. The HVAC automatically sets `currentState` to HEATING or COOLING based on the comparison between `targetTemperature` (House) and the current `temperature` (TemperatureSensor). HEATING and COOLING are mutually exclusive.
