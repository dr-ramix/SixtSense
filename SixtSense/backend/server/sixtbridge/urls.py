# sixtbridge/urls.py

from django.urls import path
from .views import (
    SixtCreateBookingAPIView,
    SixtBookingDetailAPIView,
    SixtBookingVehiclesAPIView,
    SixtBookingProtectionsAPIView,
    SixtBookingAddonsAPIView,
    SixtAssignVehicleAPIView,
    SixtAssignProtectionAPIView,
    SixtCompleteBookingAPIView,
    CarLockAPIView,
    CarUnlockAPIView,
    CarBlinkAPIView,
)

urlpatterns = [
    path("booking/", SixtCreateBookingAPIView.as_view(), name="sixt-create-booking"),
    path("booking/<str:booking_id>/", SixtBookingDetailAPIView.as_view(), name="sixt-booking-detail"),
    path("booking/<str:booking_id>/vehicles/", SixtBookingVehiclesAPIView.as_view(), name="sixt-booking-vehicles"),
    path("booking/<str:booking_id>/protections/", SixtBookingProtectionsAPIView.as_view(), name="sixt-booking-protections"),
    path("booking/<str:booking_id>/addons/", SixtBookingAddonsAPIView.as_view(), name="sixt-booking-addons"),
    path("booking/<str:booking_id>/vehicles/<str:vehicle_id>/", SixtAssignVehicleAPIView.as_view(), name="sixt-assign-vehicle"),
    path("booking/<str:booking_id>/protections/<str:package_id>/", SixtAssignProtectionAPIView.as_view(), name="sixt-assign-protection"),
    path("booking/<str:booking_id>/complete/", SixtCompleteBookingAPIView.as_view(), name="sixt-complete-booking"),

    path("car/lock/", CarLockAPIView.as_view(), name="sixt-car-lock"),
    path("car/unlock/", CarUnlockAPIView.as_view(), name="sixt-car-unlock"),
    path("car/blink/", CarBlinkAPIView.as_view(), name="sixt-car-blink"),
]
