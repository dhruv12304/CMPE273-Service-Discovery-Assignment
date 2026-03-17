"""
Discovery Client - Demonstrates client-side service discovery with random load balancing.

Steps:
1. Ask the registry for all live instances of hello-service
2. Pick one at random (client-side load balancing)
3. Call that instance's /hello endpoint
4. Repeat to show traffic spreading across instances
"""

import os
import random
import time

import requests

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:5001")
SERVICE_NAME = "hello-service"
CALLS = 5


def discover(service: str) -> list[str]:
    """Return a list of active instance addresses for the given service."""
    resp = requests.get(f"{REGISTRY_URL}/discover/{service}", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return [inst["address"] for inst in data["instances"]]


def call_random_instance(instances: list[str]) -> dict:
    """Pick a random instance and call its /hello endpoint."""
    address = random.choice(instances)
    resp = requests.get(f"{address}/hello", timeout=5)
    resp.raise_for_status()
    return address, resp.json()


if __name__ == "__main__":
    print(f"Discovering '{SERVICE_NAME}' from registry at {REGISTRY_URL}...\n")

    try:
        instances = discover(SERVICE_NAME)
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot reach the registry. Is service_registry.py running?")
        raise SystemExit(1)

    if not instances:
        print(f"No active instances of '{SERVICE_NAME}' found. Start hello_service.py first.")
        raise SystemExit(1)

    print(f"Found {len(instances)} instance(s): {instances}\n")
    print(f"Making {CALLS} calls with random instance selection:\n")
    print("-" * 55)

    for i in range(1, CALLS + 1):
        try:
            address, body = call_random_instance(instances)
            print(f"Call {i}: -> {address}")
            print(f"         {body}\n")
        except Exception as e:
            print(f"Call {i}: ERROR - {e}\n")
        time.sleep(1)
