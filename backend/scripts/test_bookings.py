import requests
import time

BASE = "http://localhost:8000"

# quick smoke test (sequential) - assumes server already running and DB available

def create_event():
    ev = {
        "title": "Test Event",
        "description": "Smoke test event",
        "start_time": "2025-12-01T10:00:00",
        "end_time": "2025-12-01T12:00:00",
        "capacity": 5,
    }
    r = requests.post(f"{BASE}/events", json=ev)
    r.raise_for_status()
    return r.json()


def book_event(event_id, user_id, seats=1):
    payload = {"user_id": user_id, "seats": seats}
    r = requests.post(f"{BASE}/events/{event_id}/book", json=payload)
    return r


if __name__ == "__main__":
    e = create_event()
    eid = e["id"]
    print("Created event", e)

    # make several bookings
    for i in range(1, 7):
        r = book_event(eid, user_id=i, seats=1)
        print(i, r.status_code, r.text)
        time.sleep(0.1)
