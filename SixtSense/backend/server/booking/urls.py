from django.urls import path
from .views import (
    BookingLinkCreateAPIView,
    BookingLinkDetailAPIView,
    BookingLinkDetailWithProfileAPIView,
    BookingLinkFullDetailAPIView,
)

urlpatterns = [
    path("booking-link/", BookingLinkCreateAPIView.as_view(), name="bookingLink-create"),
    path("booking-link/<str:booking_id>/", BookingLinkDetailAPIView.as_view(), name="bookingLink-detail"),
    path("booking-link/<str:booking_id>/detail-profile/", BookingLinkDetailWithProfileAPIView.as_view(),
         name="bookingLink-detail-profile"),
    path(
        "booking-link/<str:booking_id>/full/",
        BookingLinkFullDetailAPIView.as_view(),
        name="booking-detail-full",
    ),
]

