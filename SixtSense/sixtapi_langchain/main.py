from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sixt_client import SixtApiClient
from models import Booking, Vehicle, ChatRequest, ChatResponse, SelectedVehicle, UserPreferences, ProtectionPackage, AddonGroup, VehicleRecommendation
#from recommendation import RecommendationService
from llm_engine import run_sales_chat

import requests
from config import SIXT_BASE_URL
from enum import Enum
from pydantic import BaseModel


# tviycSQcDKNUNGb0UKyb
# in main.py, solo per debug


sixt_client = SixtApiClient()
#recommender = RecommendationService()

app = FastAPI(title="Sixt HackaTUM Backend")


###################### FOR SIMULATION OF DIFFERENT STEPS ##############################
class SalesStep(str, Enum):
    VEHICLE = "vehicle"
    PROTECTION = "protection"
    ADDONS = "addons"
    COMPLETED = "completed"


class SalesState(BaseModel):
    step: SalesStep = SalesStep.VEHICLE
    selected_vehicle_id: str | None = None
    selected_protection_id: str | None = None
    selected_addon_ids: list[str] = []


SALES_STATE_PER_BOOKING: dict[str, SalesState] = {}


def get_sales_state(booking_id: str) -> SalesState:
    if booking_id not in SALES_STATE_PER_BOOKING:
        SALES_STATE_PER_BOOKING[booking_id] = SalesState()
    return SALES_STATE_PER_BOOKING[booking_id]

##################### JUST FOR DEBUGGING ##############################

@app.get("/debug/booking/{booking_id}/vehicles_raw")
def get_vehicles_raw(booking_id: str):
    url = f"{SIXT_BASE_URL.rstrip('/')}/api/booking/{booking_id}/vehicles"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()


@app.get("/debug/booking/{booking_id}/protections_raw")
def get_protections_raw(booking_id: str):
    url = f"{SIXT_BASE_URL.rstrip('/')}/api/booking/{booking_id}/protections"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()

@app.get("/debug/booking/{booking_id}/addons_raw")
def get_addons_raw(booking_id: str):
    url = f"{SIXT_BASE_URL.rstrip('/')}/api/booking/{booking_id}/addons"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()

########################## ##############################################


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev va bene "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sixt_client = SixtApiClient()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/booking/{booking_id}", response_model=Booking)
def get_booking(booking_id: str):
    try:
        return sixt_client.get_booking(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/booking/{booking_id}/vehicles", response_model=list[SelectedVehicle])
def get_booking_vehicles(booking_id: str):
    try:
        return sixt_client.get_available_vehicles(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/booking/{booking_id}/protections", response_model=list[ProtectionPackage])
def get_booking_protections(booking_id: str):
    try:
        return sixt_client.get_available_protection_packages(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")


@app.post("/booking/{booking_id}/protections/{package_id}", response_model=Booking)
def select_protection_package(booking_id: str, package_id: str):
    state = get_sales_state(booking_id)
    try:
        booking = sixt_client.assign_protection_package(booking_id, package_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")

    state.selected_protection_id = package_id
    state.step = SalesStep.ADDONS

    return booking



@app.get("/booking/{booking_id}/addons", response_model=list[AddonGroup])
def get_booking_addons(booking_id: str):
    try:
        return sixt_client.get_available_addons(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")


@app.post("/booking/{booking_id}/vehicles/{vehicle_id}", response_model=Booking)
def select_vehicle(booking_id: str, vehicle_id: str):
    state = get_sales_state(booking_id)
    try:
        booking = sixt_client.assign_vehicle(booking_id, vehicle_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")

    state.selected_vehicle_id = vehicle_id
    state.step = SalesStep.PROTECTION

    return booking

class SelectAddonsRequest(BaseModel):
    addon_ids: list[str]


@app.post("/booking/{booking_id}/addons/select")
def select_addons(booking_id: str, body: SelectAddonsRequest):
    state = get_sales_state(booking_id)
    state.selected_addon_ids = body.addon_ids
    state.step = SalesStep.COMPLETED

    # opzionale: potresti chiamare sixt_client.complete_booking(booking_id)
    # booking = sixt_client.complete_booking(booking_id)
    # return booking

    return {
        "booking_id": booking_id,
        "step": state.step.value,
        "selected_addon_ids": state.selected_addon_ids,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    booking_id = req.booking_id
    user_message = req.message

    # Stato di vendita per questo booking
    state = get_sales_state(booking_id)

    # 1) Prendiamo sempre il booking reale (per mostrare lo stato aggiornato)
    try:
        booking = sixt_client.get_booking(booking_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")

    # 2) Chiamiamo l'LLM in base allo step corrente
    try:
        llm_result = run_sales_chat(booking_id, user_message, step=state.step.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    step = llm_result.get("step", state.step.value)
    answer = llm_result.get("answer", "")

    # 3) Prepara i campi step-specifici
    available_vehicles: list[SelectedVehicle] = []
    recs: list[VehicleRecommendation] = []
    protection_packages = None
    addons = None

    if step == "vehicle":
        # Servono i veicoli per mappare le raccomandazioni
        try:
            available_vehicles = sixt_client.get_available_vehicles(booking_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sixt API error: {e}")

        recs_data = llm_result.get("vehicle_recommendations", [])
        by_id: dict[str, SelectedVehicle] = {
            v.vehicle.id: v for v in available_vehicles
        }

        for item in recs_data:
            vid = item.get("vehicle_id")
            sv = by_id.get(vid)
            if not sv:
                continue
            recs.append(
                VehicleRecommendation(
                    selected_vehicle=sv,
                    score=float(item.get("score", 0.0)),
                    reason=item.get("reason", ""),
                )
            )

    elif step == "protection":
        protection_packages = llm_result.get("protection_packages")

    elif step == "addons":
        addons = llm_result.get("addons")

    return ChatResponse(
        answer=answer,
        booking=booking,
        step=step,
        available_vehicles=available_vehicles,
        recommendations=recs,
        protection_packages=protection_packages,
        addons=addons,
    )
