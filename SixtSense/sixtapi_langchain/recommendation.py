
####################################

# NOT USED

####################################


# recommendation.py
from typing import List
from models import SelectedVehicle, UserPreferences, VehicleRecommendation


class RecommendationService:
    def __init__(self):
        pass

    def _compute_score(
        self,
        sv: SelectedVehicle,
        prefs: UserPreferences,
    ) -> float:
        v = sv.vehicle
        pricing = sv.pricing

        score = 0.0

        # 1) Posti
        seats = v.passengersCount
        if prefs.min_seats:
            if seats >= prefs.min_seats:
                score += 2.0
            else:
                score -= 5.0

        # 2) Cambio automatico
        if prefs.wants_automatic is True:
            if (v.transmissionType or "").lower().startswith("auto"):
                score += 2.0
            else:
                score -= 3.0

        # 3) Prezzo: penalizza se sopra il max
        daily_price = pricing.displayPrice.amount
        if prefs.max_daily_price:
            if daily_price <= prefs.max_daily_price:
                score += 1.5
            else:
                # più lontano dal budget, più penalizziamo
                over = daily_price - prefs.max_daily_price
                score -= 0.1 * over

        # 4) Upgrade “qualitativo”
        if v.isMoreLuxury:
            score += 1.0
        if v.isNewCar:
            score += 0.5
        if v.isRecommended:
            score += 0.5

        return score

    def _build_reason(
        self,
        sv: SelectedVehicle,
        prefs: UserPreferences,
        score: float,
    ) -> str:
        v = sv.vehicle
        parts = [f"{v.brand} {v.model} ({v.groupType or v.acrissCode})"]

        if prefs.min_seats and v.passengersCount >= prefs.min_seats:
            parts.append(f"{v.passengersCount} seats")

        if prefs.wants_automatic and (v.transmissionType or "").lower().startswith("auto"):
            parts.append("automatic transmission")

        if v.isMoreLuxury:
            parts.append("more luxury category")
        if v.isNewCar:
            parts.append("newer car")

        daily = sv.pricing.displayPrice
        if daily.amount != 0:
            sign = "+" if daily.amount > 0 else ""
            parts.append(f"{sign}{daily.amount} {daily.currency}{daily.suffix or ''}")

        return " · ".join(parts)

    def recommend(
        self,
        vehicles: List[SelectedVehicle],
        prefs: UserPreferences,
        top_k: int = 3,
    ) -> List[VehicleRecommendation]:
        scored = []
        for sv in vehicles:
            s = self._compute_score(sv, prefs)
            reason = self._build_reason(sv, prefs, s)
            scored.append(
                VehicleRecommendation(
                    selected_vehicle=sv,
                    score=s,
                    reason=reason,
                )
            )

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
