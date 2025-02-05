import http.client
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_auth_token():
    """Fetch a new auth token and store it in config.json."""
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    audience = os.getenv("AUDIENCE")
    auth0_domain = os.getenv("AUTH0_DOMAIN")

    if not all([client_id, client_secret, audience, auth0_domain]):
        print("❌ Missing authentication details in .env")
        return None

    payload = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": "client_credentials"
    })

    headers = {'content-type': "application/json"}

    conn = http.client.HTTPSConnection(auth0_domain)
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()

    try:
        token_data = json.loads(data.decode("utf-8"))
        access_token = token_data.get("access_token")

        if access_token:
            config = load_config()
            config["ACCESS_TOKEN"] = access_token
            config["expiry"] = int(time.time()) + 86400  # Store expiry time (24 hours)
            save_config(config)
            print("✅ Auth token successfully generated and stored.")
            return access_token
        else:
            print("❌ Failed to fetch access token:", token_data)
            return None
    except json.JSONDecodeError:
        print("❌ Error decoding auth token response")
        return None
