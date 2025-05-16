from django.urls import path
from .views import tg_user_list

app_name = "user_management"

urlpatterns = [
    path("api/v1/tg-user/", ...)
]
