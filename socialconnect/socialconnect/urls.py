from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/engagement/", include("engagement.urls")),
    path("api/feed/", include("feed.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/admin/", include("adminpanel.urls")),
]
