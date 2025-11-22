from django.urls import path
from .views import MyProfileView, PublicProfileDetailView, PublicProfileListView

urlpatterns = [
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
    path("profile/<int:pk>/", PublicProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/", PublicProfileListView.as_view(), name="profiles-list"),
]