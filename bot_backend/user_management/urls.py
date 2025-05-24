from django.urls import path, include
from rest_framework import routers

from .views import TgUserViewSet

app_name = "user_management"

router = routers.DefaultRouter()

router.register("tgusers", TgUserViewSet, basename="tguser")

urlpatterns = [
    path("", include(router.urls)),
]
