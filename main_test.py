import json
import os
import time
import requests
from datetime import datetime
from math import isclose
from dotenv import load_dotenv
from scripts.parse_gpx import parse_gpx
from scripts.auth_gen import generate_auth_token

# Load environment variables from .env

load_dotenv()

CONFIG_FILE = "config.json"

# Load & save config functions
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Function to retrieve auth token
def get_token():
    config = load_config()
    if "ACCESS_TOKEN" in config and time.time() < config.get("expiry", 0):
        return config["ACCESS_TOKEN"]
    else:
        return generate_auth_token()

def get_route():
    config = load_config()
    if "ROUTE_NAME" in config and "GPX_ROUTE_PATH" in config:
        return config["ROUTE_NAME"], config["GPX_ROUTE_PATH"]
    else:
        print("❌ ERROR: ROUTE_NAME or GPX_ROUTE_PATH not found. Please set a route first.")
        return None, None

def get_tenant():
    config = load_config()
    if "TENANT_ID" in config:
        return config["TENANT_ID"]
    else:
        print("❌ ERROR: TENANT_ID not found. Please set a tenant first.")
        return None

# Function to update only necessary config values
def update_config(key, value):
    config = load_config()

    if key == "ACCESS_TOKEN":
        print("❌ ACCESS_TOKEN cannot be manually updated. Use --refresh-token instead.")

    elif key == "TENANT_ID":
        config[key] = value
        save_config(config)
        print(f"✅ Updated {key} to {value}")

    elif key == "ROUTE_NAME":
        gpx_path = f"data/{value}.gpx"

        if os.path.exists(gpx_path):
            config[key] = value
            config["GPX_ROUTE_PATH"] = gpx_path
            save_config(config)
            print(f"✅ Updated {key} to {value} and GPX_ROUTE_PATH to {gpx_path}")
        else:
            print(f"❌ GPX file 'data/{value}.gpx' does not exist. Please upload the file before using this route.")

    else:
        print(f"❌ Cannot modify {key}. Only TENANT_ID and ROUTE_NAME are allowed.")


# Function to send driver location API call
def send_driver_location(payload, url, headers):
    response = requests.post(url, json=payload, headers=headers)
    print(f"Driver Location: {payload} | Response: {response.status_code}, {response.text}")

# Function to simulate bus movement
def simulate_bus(track_points, waypoints, token):
    config = load_config()
    driver_location_url = os.getenv("API_URL")
    headers = {"Authorization": f"Bearer {token}"}

    current_waypoint_idx = 0  # Track next expected waypoint
    now = datetime.now()

    for point in track_points:
        payload = {
            "lat": point['lat'],
            "lng": point['lon'],
            "route": config.get("ROUTE_NAME"),
            "driver": str(now),
            "vehicle": "Christians Bus",
            "vehicleState": "Driving",
            "nextWaypoint": waypoints[current_waypoint_idx]['name'] if current_waypoint_idx < len(waypoints) else "None",
            "capacity": 20,
            "tenantKey": config.get("TENANT_ID")
        }

        # Check if the track point matches the next waypoint
        if current_waypoint_idx < len(waypoints):
            target_waypoint = waypoints[current_waypoint_idx]
            if isclose(point['lat'], target_waypoint['lat'], abs_tol=0.0001) and isclose(point['lon'], target_waypoint['lon'], abs_tol=0.0001):
                payload["vehicleState"] = "At Stop"
                payload["nextWaypoint"] = waypoints[current_waypoint_idx + 1]['name'] if (current_waypoint_idx + 1) < len(waypoints) else "None"
                send_driver_location(payload, driver_location_url, headers)

                print(f"🛑 Bus stopped at {target_waypoint['name']} for 5 seconds.")
                time.sleep(5)
                current_waypoint_idx += 1
            else:
                send_driver_location(payload, driver_location_url, headers)
        else:
            send_driver_location(payload, driver_location_url, headers)

        time.sleep(1)

def main_menu():
    stop = False

    while not stop:
        print("\n🚍 TikiTram Driver Simulator CLI 🚍")
        print("[1]  Get Auth Token")
        print("[2]  Refresh Auth Token")
        print("[3]  Set Tenant ID")
        print("[4]  Set Route")
        print("[5]  Get Current Route")
        print("[6]  Get Current Tenant ID")
        print("[7]  Run Bus Simulation")
        print("[0]  Exit")
        choice = input("👉 Select an option (1-8): ").strip()

        match choice:
            case "1":
                print(f"✅ Auth Token: {get_token()}")

            case "2":
                generate_auth_token()

            case "3":
                tenant_id = input("Enter new Tenant ID: ").strip()
                update_config("TENANT_ID", tenant_id)

            case "4":
                route_name = input("Enter new Route Name: ").strip()
                update_config("ROUTE_NAME", route_name)

            case "5":
                print(get_route())

            case "6":
                print(get_tenant())

            case "7":
                config = load_config()
                token = get_token()

                if not token:
                    print("❌ Cannot proceed without a valid auth token.")
                else:
                    gpx_data = parse_gpx(config.get("GPX_ROUTE_PATH"))
                    simulate_bus(gpx_data['track_points'], gpx_data['waypoints'], token)

            case "0":
                print("👋 Exiting... Have a great day!")
                stop = True  # Stops the loop

            case _:
                print("❌ Invalid choice. Please select a valid option.")

# CLI Interface
if __name__ == "__main__":
    main_menu()