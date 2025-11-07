import requests
import time
import concurrent.futures

BASE = "http://localhost:8000"


def create_event(capacity=50):
    ev = {
        "title": "Compare Strategy Event",
        "description": "Side-by-side strategy comparison",
        "start_time": "2025-12-01T10:00:00",
        "end_time": "2025-12-01T12:00:00",
        "capacity": capacity,
    }
    r = requests.post(f"{BASE}/events", json=ev)
    r.raise_for_status()
    return r.json()


def book(endpoint, event_id, user_id, seats=1):
    payload = {"user_id": user_id, "seats": seats}
    # format the endpoint template once here (endpoint is like '/events/{event_id}/book')
    url = f"{BASE}{endpoint.format(event_id=event_id)}"
    r = requests.post(url, json=payload)
    return r.status_code, r.text


def run_concurrent(endpoint, event_id, attempts=100, concurrency=20):
    print(f"Running {attempts} attempts against {endpoint} with concurrency={concurrency}")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        for i in range(attempts):
            uid = i + 1
            # pass the endpoint template and event_id; book() will format the URL
            futures.append(ex.submit(book, endpoint, event_id, uid, 1))
        for f in concurrent.futures.as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                results.append((0, str(e)))
    # tally status codes
    tally = {}
    for status, text in results:
        tally[status] = tally.get(status, 0) + 1
    return tally


if __name__ == "__main__":
    evt = create_event(capacity=50)
    eid = evt["id"]
    print("Created event", eid)

    # endpoints to test
    endpoints = [
        ("/events/{event_id}/book", "SELECT_FOR_UPDATE approach"),
        ("/events/{event_id}/book_atomic", "Atomic UPDATE approach"),
    ]

    summary = {}
    for endpoint, name in endpoints:
        # reset event? creating separate events for each run is simpler
        ev = create_event(capacity=50)
        eid = ev["id"]
        tally = run_concurrent(endpoint, eid, attempts=100, concurrency=40)
        print(f"Results for {name} ({endpoint}):", tally)
        summary[name] = tally
        time.sleep(1)

    print("Summary:\n", summary)
