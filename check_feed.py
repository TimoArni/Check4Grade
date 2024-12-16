import os
import json
import requests
import feedparser

feed_url = os.environ.get("FEED_URL")
prowl_api_key = os.environ.get("PROWL_API_KEY")
state_file = "feed_state.json"

# Parse the RSS feed
feed = feedparser.parse(feed_url)

if not feed.entries:
    print("No entries found in the feed.")
    exit(0)

# Identify the latest entry
latest_entry = feed.entries[0]
latest_id = latest_entry.get("id") or latest_entry.get("link") or latest_entry.get("title")

# Load previous state
if os.path.exists(state_file):
    with open(state_file, "r") as f:
        state = json.load(f)
else:
    state = {}

prev_latest_id = state.get("latest_id")

if latest_id != prev_latest_id:
    # New entry detected
    title = latest_entry.get("title", "New Update")
    description = latest_entry.get("summary", "No description available")

    # Prepare data for Prowl notification
    # According to the Prowl API (https://www.prowlapp.com/api.php):
    # POST to https://api.prowlapp.com/publicapi/add with form data:
    # apikey, application, event, description, priority
    data = {
        'apikey': prowl_api_key,
        'application': 'MyHAW',
        'event': title,
        'description': description,
        'priority': 0
    }

    response = requests.post("https://api.prowlapp.com/publicapi/add", data=data)

    if response.status_code == 200:
        print("Prowl notification sent successfully.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}")

    # Update state
    state["latest_id"] = latest_id
    with open(state_file, "w") as f:
        json.dump(state, f)
else:
    print("No new entry detected.")
