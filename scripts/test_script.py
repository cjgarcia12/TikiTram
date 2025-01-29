import json
import subprocess
import os
import time
import requests
from math import isclose
from datetime import datetime
from dotenv import load_dotenv, set_key
from scripts.parse_gpx import parse_gpx

# Load environment variables
load_dotenv()
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

def set_up():
    gpx_path = None
    gpx_filename = input('Type the in the CORRECT file name of the gpx file to parse (do not include .gpx)\n')

    stop1 = False
    while not stop1:
        gpx_path = f"../data/{gpx_filename}.gpx"
        if os.path.exists(gpx_path):
            print('file exist...\nsetting value in environment\n')
            os.environ["GPX_ROUTE_PATH"] = gpx_path
            set_key(dotenv_path, "GPX_ROUTE_PATH", gpx_path)
            os.environ["ROUTE_NAME"] = gpx_filename
            set_key(dotenv_path, "ROUTE_NAME", gpx_filename)
            stop1 = True
        else:
            gpx_filename = input('File does not exit, please type in a gpx file in the data folder')

    tenant_id = input("please type in the tenant id you want to use\nIf you want to use a specific id, please"
                      " type it in CAREFULLY.\nThere is no return from here\n")

    print("updating environment value\nWill now run simulation")
    os.environ["TENANT_ID"] = tenant_id
    set_key(dotenv_path, "TENANT_ID", tenant_id)


def authenticate(script_path):
    """Generate a token and update the environment."""
    choice = input("Generate a new token? (y/N): ").strip().lower()
    if choice == 'y':
        try:
            # Validate script path
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Token script not found: {script_path}")

            # Run the shell script
            output = subprocess.check_output(
                [script_path],
                stderr=subprocess.STDOUT,
                text=True
            ).strip()

            # Parse JSON and update environment
            token_data = json.loads(output)
            access_token = token_data["access_token"]
            os.environ["ACCESS_TOKEN"] = access_token
            set_key(dotenv_path, "ACCESS_TOKEN", access_token)
            print("Token updated in environment!")
            return access_token

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            print(f"Token generation failed: {e}")
            raise
    else:
        print("Using existing ACCESS_TOKEN.")
        return os.getenv("ACCESS_TOKEN")


def send_driver_location(payload, url, headers):
    """Send driver location API call."""
    response = requests.post(url, json=payload, headers=headers)
    print(f"Driver Location: {payload} | Response: {response.status_code}, {response.text}")

def simulate_bus(track_points, waypoints, token):
    driver_location_url = os.getenv("API_URL")
    headers = {"Authorization": f"Bearer {token}"}

    current_waypoint_idx = 0  # Track the index of the next expected waypoint
    last_waypoint_name = None
    now = datetime.now()

    for point in track_points:  # Iterate through track points
        payload = {
            "lat": point['lat'],
            "lng": point['lon'],
            "route": os.getenv("ROUTE_NAME"),
            "driver": str(now),
            "vehicle": "Bus_001",
            "vehicleState": "Driving",
            "nextWaypoint": waypoints[current_waypoint_idx]['name'] if current_waypoint_idx < len(waypoints) else "None",
            "capacity": 20,
            "tenantKey": os.getenv("TENANT_ID")
        }

        # Check if the current track point matches the expected waypoint
        if current_waypoint_idx < len(waypoints):
            target_waypoint = waypoints[current_waypoint_idx]
            if isclose(point['lat'], target_waypoint['lat'], abs_tol=0.0001) and \
               isclose(point['lon'], target_waypoint['lon'], abs_tol=0.0001):

                # Update payload for "At Stop" state
                payload["vehicleState"] = "At Stop"
                payload["nextWaypoint"] = waypoints[current_waypoint_idx + 1]['name'] if (current_waypoint_idx + 1) < len(waypoints) else "None"
                send_driver_location(payload, driver_location_url, headers)

                print(f"Bus stopped at {target_waypoint['name']} for 5 seconds.")
                time.sleep(5)

                # Move to the next waypoint
                current_waypoint_idx += 1
                last_waypoint_name = target_waypoint['name']
            else:
                # Send regular "Driving" payload
                send_driver_location(payload, driver_location_url, headers)
        else:
            # Send regular "Driving" payload if no more waypoints
            send_driver_location(payload, driver_location_url, headers)

        # time.sleep(1)  # Simulate delay between track points


if __name__ == "__main__":
    # Get paths from environment
    auth_script_path = os.getenv("RUN_SH_PATH")

    # Authenticate and get token
    try:
        token = authenticate(auth_script_path)
        if not token:
            raise ValueError("ACCESS_TOKEN not found. Generate a token or set it in .env.")

        choice = input("do you want to use a new gpx file and tenant id? (y/N): ")
        if choice == 'y': set_up()
        else: print('please be sure to have your eviroment values properly set up')

        # Parse GPX and simulate
        gpx_data = parse_gpx(os.getenv("GPX_ROUTE_PATH"))
        simulate_bus(gpx_data['track_points'], gpx_data['waypoints'], token, )

    except Exception as e:
        print(f"Critical error: {e}")
