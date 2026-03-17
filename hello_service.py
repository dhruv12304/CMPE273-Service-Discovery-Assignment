"""
Hello Service - A simple microservice that registers with the service registry.

Extended from ranjanr/ServiceRegistry example_service.py to include:
- A real HTTP server with /hello and /health endpoints
- Automatic registration, heartbeat, and deregistration lifecycle
"""

import argparse
import signal
import sys
import time
from threading import Thread, Event

import requests
from flask import Flask, jsonify

REGISTRY_URL = "http://localhost:5001"
HEARTBEAT_INTERVAL = 10  # seconds


def create_app(instance_name: str, port: int) -> Flask:
    app = Flask(__name__)
    address = f"http://localhost:{port}"

    @app.route("/hello")
    def hello():
        return jsonify({
            "message": f"Hello from {instance_name}!",
            "instance": address,
            "port": port,
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "instance": address})

    return app


class ServiceLifecycle:
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.address = f"http://localhost:{port}"
        self.stop_event = Event()

    def register(self):
        try:
            resp = requests.post(
                f"{REGISTRY_URL}/register",
                json={"service": self.name, "address": self.address},
                timeout=5,
            )
            if resp.status_code in (200, 201):
                print(f"[{self.name}] Registered at {self.address}")
                return True
            print(f"[{self.name}] Registration failed: {resp.text}")
            return False
        except Exception as e:
            print(f"[{self.name}] Cannot reach registry: {e}")
            return False

    def deregister(self):
        try:
            resp = requests.post(
                f"{REGISTRY_URL}/deregister",
                json={"service": self.name, "address": self.address},
                timeout=5,
            )
            if resp.status_code == 200:
                print(f"[{self.name}] Deregistered from registry")
        except Exception as e:
            print(f"[{self.name}] Deregistration error: {e}")

    def _heartbeat_loop(self):
        while not self.stop_event.wait(HEARTBEAT_INTERVAL):
            try:
                requests.post(
                    f"{REGISTRY_URL}/heartbeat",
                    json={"service": self.name, "address": self.address},
                    timeout=5,
                )
                print(f"[{self.name}] Heartbeat sent")
            except Exception as e:
                print(f"[{self.name}] Heartbeat error: {e}")

    def start_heartbeat(self):
        t = Thread(target=self._heartbeat_loop, daemon=True)
        t.start()

    def shutdown(self, *_):
        print(f"\n[{self.name}] Shutting down...")
        self.stop_event.set()
        self.deregister()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello microservice")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--name", type=str, default="hello-service")
    args = parser.parse_args()

    lifecycle = ServiceLifecycle(args.name, args.port)

    signal.signal(signal.SIGINT, lifecycle.shutdown)
    signal.signal(signal.SIGTERM, lifecycle.shutdown)

    if not lifecycle.register():
        print("Could not register with registry. Is service_registry.py running?")
        sys.exit(1)

    lifecycle.start_heartbeat()

    app = create_app(args.name, args.port)
    print(f"[{args.name}] HTTP server listening on port {args.port}")
    app.run(host="0.0.0.0", port=args.port, use_reloader=False, threaded=True)
