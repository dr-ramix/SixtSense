from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import Profile
from .serializers import ProfileSerializer


class MyProfileView(APIView):
    """
    /api/profile/me/
    Auth required.
    GET   -> return current user's profile
    PUT   -> full update
    PATCH -> partial update
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request):
        # Ensure profile exists (in case signal didn't run)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return profile

    def get(self, request):
        profile = self.get_object(request)
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        profile = self.get_object(request)
        serializer = ProfileSerializer(
            profile,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        profile = self.get_object(request)
        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicProfileDetailView(APIView):
    """
    /api/profile/<id>/
    NO auth required.
    GET -> return profile by id
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)


class PublicProfileListView(APIView):
    """
    /api/profiles/
    NO auth required.
    GET -> list all profiles
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        profiles = Profile.objects.all().select_related("user")
        serializer = ProfileSerializer(profiles, many=True, context={"request": request})
        return Response(serializer.data)
