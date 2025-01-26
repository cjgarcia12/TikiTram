# **TikiTram Simulation Script**

## **Overview**
This project simulates a bus operating along a predefined route using GPX data. The simulation interacts with an API to send updates about the vehicle's position, manage stops, and handle startup and shutdown processes.

---

## **Features**

### **1. Parsing GPX Data**
- **`parse_gpx.py`**:
  - Extracts:
    - **Waypoints (`<wpt>`)**: Represent bus stops.
    - **Track Points (`<trkpt>`)**: Represent the path the bus follows between stops.
  - Returns the data as a dictionary with `waypoints` and `track_points`.

---

### **2. Simulating Movement**
- **`simulate_bus` Function**:
  - Iterates through the `track_points` and sends:
    - **Driving Updates**: Current position and state (`Driving`) of the vehicle.
    - **Stop Updates**: Indicates when the vehicle reaches a waypoint (`At Stop`).
  - Adds delays to simulate real-time behavior.

---

### **2. Authentication(*CURRENT NOT IN USE*)**
- The script authenticates with the API using the provided username and password.
- An access token is retrieved and used for all subsequent API calls.

---

### **4. API Interaction**
- **Driver Location API**:
  - **POST**:
    - Sends real-time updates about the vehicle’s location and state.
    - Payload includes:
      - Latitude and longitude.
      - Current route, driver, and vehicle identifiers.
      - Vehicle state (`Driving` or `At Stop`).
      - The next waypoint, capacity, and tenant key.
  - Simulated responses are printed for debugging and testing (Logging can be implemented if needed).

---