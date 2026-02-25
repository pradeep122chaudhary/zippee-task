from django.urls import path

from .views import LoginAPIView, RegisterAPIView, UserDataAPIView


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("users/", UserDataAPIView.as_view(), name="user-data"),
]
