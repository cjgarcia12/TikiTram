from dotenv import load_dotenv
import os
import time
import requests
from math import isclose
from scripts.parse_gpx import parse_gpx

# Load environment variables
load_dotenv()

"""We dont need this for now, if we later want to use this at a larger scale
it might be helpful to have this"""
# def authenticate(auth_url, client_id, client_secret):
#     """Generate a token using client credentials."""
#     payload = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "grant_type": "client_credentials"
#     }
#     response = requests.post(auth_url, data=payload)
#     if response.status_code == 200:
#         print("Authentication successful!")
#         return response.json().get("access_token")
#     else:
#         raise Exception(f"Authentication failed: {response.status_code}, {response.text}")


def send_driver_location(payload, url, headers):
    """Send driver location API call."""
    response = requests.post(url, json=payload, headers=headers)
    print(f"Driver Location: {payload} | Response: {response.status_code}, {response.text}")


def simulate_bus(track_points, waypoints, token):
    """Simulate bus movement using track points and handle waypoints."""
    driver_location_url = os.getenv("API_URL")
    if not driver_location_url:
        raise Exception("API_URL not found in env")

    headers = {"Authorization": f"Bearer {token}"}

    for i, point in enumerate(track_points):
        # Prepare the payload for the current state
        payload = {
            "lat": point['lat'],
            "lng": point['lon'],
            "route": "Riverlights_Express",
            "driver": "Driver_001",
            "vehicle": "Bus_001",
            "vehicleState": "Driving",
            "nextWaypoint": waypoints[i + 1]['name'] if i + 1 < len(waypoints) else None,
            "capacity": 20,
            "tenantKey": "Christians_Tenant"
        }
        send_driver_location(payload, driver_location_url, headers)

        # Check if the bus is near a waypoint
        for waypoint in waypoints:
            if isclose(point['lat'], waypoint['lat'], abs_tol=0.0001) and \
               isclose(point['lon'], waypoint['lon'], abs_tol=0.0001):
                # Update payload for "At Stop" state
                payload["vehicleState"] = "At Stop"
                payload["nextWaypoint"] = None
                send_driver_location(payload, driver_location_url, headers)

                # Simulate stop duration
                print(f"Bus stopped at {waypoint['name']} for 5 seconds.")
                time.sleep(5)

        # Simulate delay between track points
        if i < len(track_points) - 1:
            time.sleep(2)


if __name__ == "__main__":
    # Parse the GPX file
    gpx_data = parse_gpx('../data/Riverlights_Express.gpx')

    # Retrieve token from environment variables
    token = os.getenv("ACCESS_TOKEN")
    if not token:
        raise Exception("ACCESS_TOKEN not found in environment variables.")

    # Simulate the bus movement
    simulate_bus(gpx_data['track_points'], gpx_data['waypoints'], token)
