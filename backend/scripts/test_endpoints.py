"""Simple API smoke-test script for the Event Booking Microservice.

Usage:
    python scripts/test_endpoints.py

It will:
 - GET /health
 - GET /events (should be empty or a list)
 - POST /events to create a sample event
 - GET /events to verify creation

This script uses `requests` and expects the backend to be running at http://127.0.0.1:8000
"""
import sys
import time
import json

import requests

BASE = "http://127.0.0.1:8000"


def pretty_print(title, data):
    print("\n--- {} ---".format(title))
    try:
        print(json.dumps(data, indent=2, default=str))
    except Exception:
        print(data)


def main():
    print("Running API smoke tests against", BASE)

    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        pretty_print("GET /health", r.json())
    except Exception as e:
        print("Failed to reach /health:", e)
        sys.exit(2)

    # list events
    r = requests.get(f"{BASE}/events")
    try:
        pretty_print("GET /events (before)", r.json())
    except Exception:
        print("GET /events returned non-json or failed: status", r.status_code)

    # create sample event
    sample = {
        "title": "Smoke Test Event",
        "description": "Created by test_endpoints.py",
        "start_time": (time.strftime("%Y-%m-%dT%H:%M:00", time.localtime(time.time() + 3600))),
        "end_time": (time.strftime("%Y-%m-%dT%H:%M:00", time.localtime(time.time() + 7200))),
        "capacity": 10,
    }

    r = requests.post(f"{BASE}/events", json=sample)
    if r.status_code not in (200, 201):
        print("Failed to create event: status", r.status_code, r.text)
        sys.exit(3)

    pretty_print("POST /events -> created", r.json())
    created = r.json()

    # list events again
    r = requests.get(f"{BASE}/events")
    pretty_print("GET /events (after)", r.json())

    # get the event by id
    event_id = created.get("id")
    if event_id:
        r = requests.get(f"{BASE}/events/{event_id}")
        pretty_print(f"GET /events/{event_id}", r.json())
    else:
        print("No id returned from create response; skipping GET by id.")

    print("\nSmoke tests completed successfully.")


if __name__ == "__main__":
    main()
