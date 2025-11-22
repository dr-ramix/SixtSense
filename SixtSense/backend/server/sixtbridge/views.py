# sixtbridge/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .sixt_api import (
    create_booking,
    get_booking,
    get_vehicles,
    get_protections,
    get_addons,
    assign_vehicle,
    assign_protection,
    complete_booking,
    car_lock,
    car_unlock,
    car_blink,
)


class SixtCreateBookingAPIView(APIView):
    """
    POST /sixt/booking/
    -> forwards to SIXT POST /api/booking
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            sixt_data = create_booking(request.data)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (create booking): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_201_CREATED)


class SixtBookingDetailAPIView(APIView):
    """
    GET /sixt/booking/<booking_id>/
    -> SIXT GET /api/booking/<BOOKING_ID>
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id, *args, **kwargs):
        try:
            sixt_data = get_booking(booking_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (get booking): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtBookingVehiclesAPIView(APIView):
    """
    GET /sixt/booking/<booking_id>/vehicles/
    -> SIXT GET /api/booking/<BOOKING_ID>/vehicles
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id, *args, **kwargs):
        try:
            sixt_data = get_vehicles(booking_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (get vehicles): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtBookingProtectionsAPIView(APIView):
    """
    GET /sixt/booking/<booking_id>/protections/
    -> SIXT GET /api/booking/<BOOKING_ID>/protections
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id, *args, **kwargs):
        try:
            sixt_data = get_protections(booking_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (get protections): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtBookingAddonsAPIView(APIView):
    """
    GET /sixt/booking/<booking_id>/addons/
    -> SIXT GET /api/booking/<BOOKING_ID>/addons
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, booking_id, *args, **kwargs):
        try:
            sixt_data = get_addons(booking_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (get addons): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtAssignVehicleAPIView(APIView):
    """
    POST /sixt/booking/<booking_id>/vehicles/<vehicle_id>/
    -> SIXT POST /api/booking/<BOOKING_ID>/vehicles/<VEHICLE_ID>
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, booking_id, vehicle_id, *args, **kwargs):
        try:
            sixt_data = assign_vehicle(booking_id, vehicle_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (assign vehicle): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtAssignProtectionAPIView(APIView):
    """
    POST /sixt/booking/<booking_id>/protections/<package_id>/
    -> SIXT POST /api/booking/<BOOKING_ID>/protections/<PACKAGE_ID>
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, booking_id, package_id, *args, **kwargs):
        try:
            sixt_data = assign_protection(booking_id, package_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (assign protection): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class SixtCompleteBookingAPIView(APIView):
    """
    POST /sixt/booking/<booking_id>/complete/
    -> SIXT POST /api/booking/<BOOKING_ID>/complete
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, booking_id, *args, **kwargs):
        try:
            sixt_data = complete_booking(booking_id)
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (complete booking): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class CarLockAPIView(APIView):
    """
    POST /sixt/car/lock/
    -> SIXT POST /api/car/lock
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            sixt_data = car_lock()
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (car lock): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class CarUnlockAPIView(APIView):
    """
    POST /sixt/car/unlock/
    -> SIXT POST /api/car/unlock
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            sixt_data = car_unlock()
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (car unlock): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)


class CarBlinkAPIView(APIView):
    """
    POST /sixt/car/blink/
    -> SIXT POST /api/car/blink
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            sixt_data = car_blink()
        except Exception as e:
            return Response(
                {"detail": f"Error talking to SIXT (car blink): {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(sixt_data, status=status.HTTP_200_OK)
