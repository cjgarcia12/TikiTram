import time
import requests
from math import isclose

from scripts.parse_gpx import parse_gpx


def send_current_state(payload, url, headers):
    response = requests.post(url, json=payload, headers=headers)
    print(f"Current State: {payload} | Response: {response.status_code}")
    return response

def send_at_stop(payload, url, headers):
    response = requests.post(url, json=payload, headers=headers)
    print(f"At Stop: {payload} | Response: {response.status_code}")
    return response

def simulate_bus(track_points, waypoints, token):
    current_state_url = 'https://placeholder.com/current_state'
    at_stop_url = 'https://placeholder.com/at_stop'
    headers = {"Authorization": f"Bearer {token}"}

    for i, point in enumerate(track_points):
        # Send current state API call
        payload = {
            "tenant_id": "12345",
            "vehicle_id": "001",
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
                    "stop_name": waypoint['name'],
                    "latitude": waypoint['lat'],
                    "longitude": waypoint['lon']
                }
                send_at_stop(stop_payload, at_stop_url, headers)

        # Simulate delay between track points
        if i < len(track_points) - 1:
            time.sleep(2) # can adjust if needed

if __name__ == "__main__":
    # Parse the gpx
    gpx_data = parse_gpx('../data/Riverlights_Express.gpx')
    print(gpx_data)

    # We would put the token here for authentication
    token = 'placeholder_token'

    # Simulate the bus movement
    simulate_bus(gpx_data['track_points'], gpx_data['waypoints'], token)

