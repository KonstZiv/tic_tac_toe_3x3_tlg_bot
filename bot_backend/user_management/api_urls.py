from django.urls import path, include
from rest_framework_nested import routers

from tictactoe.views import TicTacToePropositionViewSet
from .views import TgUserViewSet, WebUserViewSet

app_name = "api_user_management"

router = routers.SimpleRouter()
router.register("tgusers", TgUserViewSet, basename="tgusers")

router.register("webusers", WebUserViewSet, basename="webusers")

tgusers_router = routers.NestedSimpleRouter(router, "tgusers", lookup="tguser")
tgusers_router.register(
    "tictactoe-propositions",
    TicTacToePropositionViewSet,
    basename="tguser-tictactoe-propositions",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(tgusers_router.urls)),
]
