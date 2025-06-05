from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from user_management.models import TgUser
from .models import TicTacToeProposition
from .serializers import TicTacToePropositionSerializer


class TicTacToePropositionViewSet(viewsets.ModelViewSet):
    serializer_class = TicTacToePropositionSerializer

    def get_queryset(self):
        tguser_id = self.kwargs.get('tguser_pk')
        content_type = ContentType.objects.get_for_model(TgUser)

        # Базовий запит для активних пропозицій, де TgUser є player1 або player2
        queryset = TicTacToeProposition.objects.filter(
            Q(player1_content_type=content_type, player1_object_id=tguser_id) |
            Q(player2_content_type=content_type, player2_object_id=tguser_id),
            is_active=True
        )

        # Фільтрація за параметрами
        status_filter = self.request.query_params.get('status')
        is_player1 = self.request.query_params.get('is_player1')
        is_accepted = self.request.query_params.get('is_accepted')
        expired = self.request.query_params.get('expired')

        if status_filter:
            valid_statuses = [s[0] for s in TicTacToeProposition._meta.get_field('status').choices]
            statuses = status_filter.split(',')
            invalid_statuses = [s for s in statuses if s not in valid_statuses]
            if invalid_statuses:
                raise ValidationError(f"Invalid status values: {invalid_statuses}")
            queryset = queryset.filter(status__in=statuses)

        if is_player1 is not None:
            is_player1 = is_player1.lower() == 'true'
            if is_player1:
                queryset = queryset.filter(player1_content_type=content_type, player1_object_id=tguser_id)
            else:
                queryset = queryset.filter(player2_content_type=content_type, player2_object_id=tguser_id)

        if is_accepted is not None:
            is_accepted = is_accepted.lower() == 'true'
            if is_accepted:
                queryset = queryset.filter(accepted_at__isnull=False)
            else:
                queryset = queryset.filter(accepted_at__isnull=True)

        if expired is not None:
            expired = expired.lower() == 'true'
            if expired:
                queryset = queryset.filter(expires_at__lt=timezone.now())
            else:
                queryset = queryset.filter(expires_at__gte=timezone.now())

        return queryset.select_related('player1_content_type', 'player2_content_type')

    def get_object(self):
        tguser_id = self.kwargs.get('tguser_pk')
        proposition_id = self.kwargs.get('pk')
        content_type = ContentType.objects.get_for_model(TgUser)

        try:
            proposition = TicTacToeProposition.objects.get(
                Q(player1_content_type=content_type, player1_object_id=tguser_id) |
                Q(player2_content_type=content_type, player2_object_id=tguser_id),
                pk=proposition_id,
                is_active=True
            )
        except TicTacToeProposition.DoesNotExist:
            raise NotFound("Proposition not found or not active for this user.")
        return proposition

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tguser_pk'] = self.kwargs.get('tguser_pk')
        return context

    def create(self, request, tguser_pk=None):
        """Створює нову пропозицію для TgUser."""
        try:
            TgUser.objects.get(id=tguser_pk)
        except TgUser.DoesNotExist:
            raise NotFound("TgUser not found.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, tguser_pk=None, pk=None):
        """Деактивує пропозицію (is_active = False)."""
        proposition = self.get_object()
        proposition.is_active = False
        proposition.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, tguser_pk=None, pk=None, partial=False):
        """Оновлює пропозицію (PUT або PATCH)."""
        proposition = self.get_object()
        serializer = self.get_serializer(proposition, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
