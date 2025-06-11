from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from user_management.models import TgUser
from .models import TicTacToeProposition
from .serializers import TicTacToePropositionGetSerializer, TicTacToePropositionFilterSerializer, \
    TicTacToePropositionPostSerializer


class TicTacToePropositionViewSet(viewsets.ModelViewSet):
    serializer_class = TicTacToePropositionGetSerializer

    @extend_schema(
        parameters=[TicTacToePropositionFilterSerializer],
        description="Retrieve Tic Tac Toe propositions for a specific TgUser.",

    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        tguser_id = self.kwargs.get('tguser_pk')
        content_type = ContentType.objects.get_for_model(TgUser)

        # Базовий запит для активних пропозицій, де TgUser є player1 або player2
        queryset = TicTacToeProposition.objects.filter(
            Q(player1_content_type=content_type, player1_object_id=tguser_id) |
            Q(player2_content_type=content_type, player2_object_id=tguser_id),
            is_active=True
        )
        filter_serializer = TicTacToePropositionFilterSerializer(data=self.request.query_params)
        is_valid_result = filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        # Фільтрація
        if 'statuses' in filters and filters["statuses"]:
            queryset = queryset.filter(status__in=filters['statuses'])

        if filters['is_player1'] is not None:
            if filters['is_player1']:
                queryset = queryset.filter(player1_content_type=content_type, player1_object_id=tguser_id)
            else:
                queryset = queryset.filter(player2_content_type=content_type, player2_object_id=tguser_id)

        if filters['expired'] is not None:
            if filters['expired']:
                queryset = queryset.filter(expires_at__lt=timezone.now())
            else:
                queryset = queryset.filter(expires_at__gte=timezone.now())

        queryset = queryset.select_related('player1_content_type', 'player2_content_type')
        return queryset

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
        context["player1_content_type"] = ContentType.objects.get_for_model(TgUser)
        context["player1_object_id"] = self.kwargs.get('tguser_pk')
        try:
            context["player2_content_type"] = ContentType.objects.get_for_model(TgUser)
            context["player1_object"] = TgUser.objects.get(id=context["player1_object_id"])
        except TgUser.DoesNotExist:
            raise NotFound("TgUser not found.")
        return context

    def get_serializer(self, *args, **kwargs):
        """Повертає серіалізатор для отримання пропозицій."""
        kwargs['context'] = self.get_serializer_context()
        if self.action in ['create', 'update']:
            return TicTacToePropositionPostSerializer(*args, **kwargs)
        elif self.action in ['list', 'retrieve']:
            return TicTacToePropositionGetSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

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
