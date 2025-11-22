from typing import List
import requests
from config import SIXT_BASE_URL
from models import Booking, SelectedVehicle, ProtectionPackage, AddonGroup


class SixtApiClient:
    def __init__(self, base_url: str = SIXT_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_booking(self, booking_id: str) -> Booking:
        url = self._url(f"/api/booking/{booking_id}")
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return Booking.model_validate(data)

    def get_available_vehicles(self, booking_id: str) -> List[SelectedVehicle]:
        url = self._url(f"/api/booking/{booking_id}/vehicles")
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # data è un dict con chiave "deals"
        deals = data.get("deals", [])
        if not isinstance(deals, list):
            raise ValueError(
                f"Unexpected /vehicles response shape: 'deals' is not a list (type={type(deals)})"
            )

        return [SelectedVehicle.model_validate(d) for d in deals]

    def assign_vehicle(self, booking_id: str, vehicle_id: str) -> Booking:
        url = self._url(f"/api/booking/{booking_id}/vehicles/{vehicle_id}")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return Booking.model_validate(resp.json())
    
    def get_available_protection_packages(self, booking_id: str) -> list[ProtectionPackage]:
        url = self._url(f"/api/booking/{booking_id}/protections")
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        packages = data.get("protectionPackages", [])
        return [ProtectionPackage.model_validate(p) for p in packages]

    def get_available_addons(self, booking_id: str) -> list[AddonGroup]:
        url = self._url(f"/api/booking/{booking_id}/addons")
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        groups = data.get("addons", [])
        return [AddonGroup.model_validate(g) for g in groups]

    def assign_protection_package(self, booking_id: str, package_id: str) -> Booking:
        """
        Usa l'endpoint:
        POST /api/booking/{BOOKING_ID}/protections/{PACKAGE_ID}
        """
        url = self._url(f"/api/booking/{booking_id}/protections/{package_id}")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return Booking.model_validate(resp.json())


    def complete_booking(self, booking_id: str) -> Booking:
        url = self._url(f"/api/booking/{booking_id}/complete")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return Booking.model_validate(resp.json())

    def lock_car(self):
        url = self._url("/api/car/lock")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def unlock_car(self):
        url = self._url("/api/car/unlock")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def blink_car(self):
        url = self._url("/api/car/blink")
        resp = requests.post(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
