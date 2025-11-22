import os
import requests

# You can move this to settings or env var if needed
SIXT_BASE_URL = os.getenv("SIXT_BASE_URL", "https://hackatum25.sixt.io")


def create_booking(payload: dict) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def get_booking(booking_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_vehicles(booking_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/vehicles"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_protections(booking_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/protections"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_addons(booking_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/addons"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def assign_vehicle(booking_id: str, vehicle_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/vehicles/{vehicle_id}"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()


def assign_protection(booking_id: str, package_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/protections/{package_id}"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()


def complete_booking(booking_id: str) -> dict:
    url = f"{SIXT_BASE_URL}/api/booking/{booking_id}/complete"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()


def car_lock() -> dict:
    url = f"{SIXT_BASE_URL}/api/car/lock"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()


def car_unlock() -> dict:
    url = f"{SIXT_BASE_URL}/api/car/unlock"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()


def car_blink() -> dict:
    url = f"{SIXT_BASE_URL}/api/car/blink"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    return response.json()
