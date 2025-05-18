from django.urls import path, include
from rest_framework import routers

from .views import TgUserViewSet

app_name = "api_user_management"

router = routers.DefaultRouter()
# Register the TgUserViewSet with the router
router.register("tgusers", TgUserViewSet, basename="tgusers")


urlpatterns = [
    path("", include(router.urls)),
]
