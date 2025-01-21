# **TikiTram Simulation Script**

## **Overview**
This project simulates a bus operating along a predefined route using GPX data. The simulation interacts with an API to send updates about the vehicle's position, manage stops, and handle startup and shutdown processes.

---

## **How the Code Works**

### **1. Parsing GPX Data**
- The `parse_gpx.py` script reads the GPX file to extract:
  - **Waypoints (`<wpt>`)**: Represent bus stops.
  - **Track Points (`<trkpt>`)**: Represent the path the bus follows between stops.
- The parsed data is returned as a dictionary with `waypoints` and `track_points`.

### **2. Authentication**
- The script authenticates with the API using the provided username and password.
- An access token is retrieved and used for all subsequent API calls.

### **3. Startup**
- The `startup_vehicle` function sends a request to activate the vehicle on the specified route. This initializes the vehicle in the backend system and prepares it for tracking.

### **4. Simulating Movement**
- The `simulate_bus` function:
  1. Iterates through the track points and sends location updates (`Current State` API calls).
  2. Detects when the vehicle reaches a waypoint (bus stop) and sends an `At Stop` API call.
  3. Adds a delay (`time.sleep`) between updates to mimic real-time movement.

### **5. Shutdown**
- The `shutdown_vehicle` function sends a request to deactivate the vehicle. This signals the end of the route and marks the vehicle as inactive.


## **Next Steps**
1. Add structured logging to track simulation progress and API responses.
2. Extend functionality for simultaneous testing of multiple vehicles/routes.
3. Adjust for multiple GPX files to be read