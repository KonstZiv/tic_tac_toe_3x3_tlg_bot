from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import TgUser, TgStartAttempt
from .serializers import TgUserSerializer


class TgUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer

    def list(self, request, *args, **kwargs):
        """
        Restricted this action.
        Return status code 405 - Method Not Allowed
        """
        return self.http_method_not_allowed(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Custom logic for POST request:
        - Check if TgUser with given tg_id exists.
        - If exists, update fields that differ from the request data and create a new TgStartAttempt.
        - If does not exist, create a new TgUser (TgStartAttempt created via TgUser.save()).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Отримуємо tg_id із запиту
        tg_id = validated_data.get('tg_id')

        try:
            with transaction.atomic():
                # Шукаємо існуючого користувача за tg_id
                existing_user = TgUser.objects.get(tg_id=tg_id)

                # Оновлюємо поля, які відрізняються
                update_fields = []
                for field, value in validated_data.items():
                    current_value = getattr(existing_user, field)
                    if current_value != value:
                        setattr(existing_user, field, value)
                        update_fields.append(field)

                # Зберігаємо зміни, якщо є що оновлювати
                if update_fields:
                    existing_user.save(update_fields=update_fields)

                # Створюємо новий TgStartAttempt
                TgStartAttempt.objects.create(tg_user=existing_user)
                # Серіалізуємо оновлений об’єкт для відповіді
                serializer = self.get_serializer(existing_user)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

        except ObjectDoesNotExist:
            # Якщо користувача немає, створюємо нового
            # Метод save() моделі TgUser автоматично створить TgStartAttempt
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
