# users/urls.py
from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, VerifyEmailView, 
    PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView,
    UserProfileView, MyProfileView, FollowUserView, FollowersListView, FollowingListView,
    AvatarUploadView, DiscoverUsersView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
    
    # Profile endpoints
    path("me/", MyProfileView.as_view(), name="my_profile"),
    path("me/avatar/", AvatarUploadView.as_view(), name="avatar_upload"),
    path("<int:user_id>/", UserProfileView.as_view(), name="user_profile"),
    path("<int:user_id>/follow/", FollowUserView.as_view(), name="follow_user"),
    path("<int:user_id>/followers/", FollowersListView.as_view(), name="user_followers"),
    path("<int:user_id>/following/", FollowingListView.as_view(), name="user_following"),
    path("discover/", DiscoverUsersView.as_view(), name="discover_users"),
]
