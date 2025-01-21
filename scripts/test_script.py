import time
import requests
from math import isclose
from scripts.parse_gpx import parse_gpx


def authenticate(auth_url, username, password):
    """Authenticate and retrieve a token."""
    payload = {"username": username, "password": password}
    response = requests.post(auth_url, json=payload)
    if response.status_code == 200:
        print("Authentication successful!")
        return response.json().get("access_token")
    else:
        raise Exception(f"Authentication failed: {response.status_code}, {response.text}")


def startup_vehicle(token, startup_url, tenant_id, vehicle_id, route_id):
    """Enable the vehicle on a route."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "tenant_id": tenant_id,
        "vehicle_id": vehicle_id,
        "route_id": route_id
    }
    response = requests.post(startup_url, json=payload, headers=headers)
    print(f"Startup: {payload} | Response: {response.status_code}, {response.text}")


def shutdown_vehicle(token, shutdown_url, tenant_id, vehicle_id, route_id):
    """Take the vehicle offline."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "tenant_id": tenant_id,
        "vehicle_id": vehicle_id,
        "route_id": route_id
    }
    response = requests.post(shutdown_url, json=payload, headers=headers)
    print(f"Shutdown: {payload} | Response: {response.status_code}, {response.text}")


def send_current_state(payload, url, headers):
    """Send current state API call."""
    response = requests.post(url, json=payload, headers=headers)
    print(f"Current State: {payload} | Response: {response.status_code}")


def send_at_stop(payload, url, headers):
    """Send At Stop API call."""
    response = requests.post(url, json=payload, headers=headers)
    print(f"At Stop: {payload} | Response: {response.status_code}")


def simulate_bus(track_points, waypoints, token):
    """Simulate bus movement using track points and handle waypoints."""
    current_state_url = "https://placeholder.com/current_state"
    at_stop_url = "https://placeholder.com/at_stop"
    headers = {"Authorization": f"Bearer {token}"}

    for i, point in enumerate(track_points):
        # Send current state API call
        payload = {
            "tenant_id": "12345",
            "vehicle_id": "001",
            "route_id": "Riverlights_Express",
            "latitude": point['lat'],
            "longitude": point['lon'],
            "timestamp": point['time']
        }
        send_current_state(payload, current_state_url, headers)

        # Check if the bus is near a waypoint
        for waypoint in waypoints:
            if isclose(point['lat'], waypoint['lat'], abs_tol=0.0001) and \
               isclose(point['lon'], waypoint['lon'], abs_tol=0.0001):
                # Send "At Stop" API call for waypoint
                stop_payload = {
                    "tenant_id": "12345",
                    "vehicle_id": "001",
                    "route_id": "Riverlights_Express",
                    "stop_name": waypoint['name'],
                    "latitude": waypoint['lat'],
                    "longitude": waypoint['lon']
                }
                send_at_stop(stop_payload, at_stop_url, headers)

        # Simulate delay between track points
        if i < len(track_points) - 1:
            time.sleep(2)  # Adjust if needed


if __name__ == "__main__":
    # Parse the GPX file
    gpx_data = parse_gpx('../data/Riverlights_Express.gpx')

    # Authenticate and retrieve a token
    auth_url = "https://placeholder.com/auth"
    username = "placeholder_username"
    password = "placeholder_password"
    token = authenticate(auth_url, username, password)

    # Startup the vehicle
    startup_url = "https://placeholder.com/startup"
    startup_vehicle(token, startup_url, "12345", "001", "Riverlights_Express")

    # Simulate the bus movement
    simulate_bus(gpx_data['track_points'], gpx_data['waypoints'], token)

    # Shutdown the vehicle
    shutdown_url = "https://placeholder.com/shutdown"
    shutdown_vehicle(token, shutdown_url, "12345", "001", "Riverlights_Express")
