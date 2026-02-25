from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(("config.v1_urls", "api"), namespace="v1")),
]
