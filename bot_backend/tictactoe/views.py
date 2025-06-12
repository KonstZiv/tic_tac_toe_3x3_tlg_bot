from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from user_management.models import TgUser
from .models import TicTacToeProposition
from .serializers import (
    TicTacToePropositionGetSerializer,
    TicTacToePropositionFilterSerializer,
    TicTacToePropositionPostSerializer,
)


class TicTacToePropositionViewSet(viewsets.ModelViewSet):
    """Manage tic-tac-toe offers for Telegram users.
    Allows you to create, receive, update, and deactivate offers.
    """

    CONTENT_TYPE_TG = ContentType.objects.get_for_model(TgUser)

    @extend_schema(
        parameters=[
            TicTacToePropositionFilterSerializer,
            OpenApiParameter(
                name="tguser_pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="TgUser.id of the telegram-user for whom work with TicTacToeProposition is returned",
                required=True,
            ),
        ],
        description=(
            "Returns a list of active tic-tac-toe offers for the specified Telegram user. "
            "Supports filtering by status, player role, and expiration."
        ),
        responses={
            200: TicTacToePropositionGetSerializer(many=True),
            404: None,
        },
        examples=[
            OpenApiExample(
                name="Successful response.",
                value=[
                    {
                        "id": 1,
                        "player1": {
                            "id": 12345678,
                            "first_name": "John",
                            "last_name": None,
                            "username": "@john",
                        },
                        "player2": None,
                        "player1_first": True,
                        "player1_sign": "❌",
                        "player2_sign": "⭕",
                        "created_at": "2025-06-11T15:00:00Z",
                        "accepted_at": None,
                        "status": "incomplete",
                        "expires_at": "2025-06-18T12:00:00Z",
                        "deep_links": {
                            "telegram": "https://t.me/YourBotName?start=proposition_1",
                            "web": "https://yourapp.com/tictactoe/proposition/1",
                        },
                    }
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tguser_pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="TgUser.id of the telegram-user for whom work with TicTacToeProposition.",
                required=True,
            ),
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="TicTacToeProposition.id of the proposition to retrieve.",
                required=True,
            ),
        ],
        description="Returns details of a specific active offer for the specified user",
        responses={
            200: TicTacToePropositionGetSerializer,
            404: None,
        },
        examples=[
            OpenApiExample(
                name="Successful response.",
                value={
                    "id": 1,
                    "player1": {
                        "id": 12345678,
                        "first_name": "John",
                        "last_name": None,
                        "username": "@john",
                    },
                    "player2": None,
                    "player1_first": True,
                    "player1_sign": "❌",
                    "player2_sign": "⭕",
                    "created_at": "2025-06-11T15:00:00Z",
                    "accepted_at": None,
                    "status": "pending",
                    "expires_at": "2025-06-18T12:00:00Z",
                    "deep_links": {
                        "telegram": "https://t.me/YourBotName?start=proposition_1",
                        "web": "https://yourapp.com/tictactoe/proposition/1",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[TicTacToeProposition]:
        tguser_id = self.kwargs.get("tguser_pk")

        # Basic query for active offers where TgUser is player1 or player2
        queryset = TicTacToeProposition.objects.filter(
            Q(player1_content_type=self.CONTENT_TYPE_TG, player1_object_id=tguser_id)
            | Q(player2_content_type=self.CONTENT_TYPE_TG, player2_object_id=tguser_id),
            is_active=True,
        )
        filter_serializer = TicTacToePropositionFilterSerializer(
            data=self.request.query_params
        )
        is_valid_result = filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        # Apply filters based on the validated data
        if "statuses" in filters and filters["statuses"]:
            queryset = queryset.filter(status__in=filters["statuses"])

        if filters["is_player1"] is not None:
            if filters["is_player1"]:
                queryset = queryset.filter(
                    player1_content_type=self.CONTENT_TYPE_TG,
                    player1_object_id=tguser_id,
                )
            else:
                queryset = queryset.filter(
                    player2_content_type=self.CONTENT_TYPE_TG,
                    player2_object_id=tguser_id,
                )

        if filters["expired"] is not None:
            if filters["expired"]:
                queryset = queryset.filter(expires_at__lt=timezone.now())
            else:
                queryset = queryset.filter(expires_at__gte=timezone.now())

        queryset = queryset.select_related(
            "player1_content_type", "player2_content_type"
        )
        return queryset

    def get_object(self) -> TicTacToeProposition:
        tguser_id = self.kwargs.get("tguser_pk")
        proposition_id = self.kwargs.get("pk")

        try:
            proposition = TicTacToeProposition.objects.get(
                Q(
                    player1_content_type=self.CONTENT_TYPE_TG,
                    player1_object_id=tguser_id,
                )
                | Q(
                    player2_content_type=self.CONTENT_TYPE_TG,
                    player2_object_id=tguser_id,
                ),
                pk=proposition_id,
                is_active=True,
            )
        except TicTacToeProposition.DoesNotExist:
            raise NotFound("Proposition not found or not active for this user.")
        return proposition

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["player1_content_type"] = self.CONTENT_TYPE_TG
        context["player1_object_id"] = self.kwargs.get("tguser_pk")
        try:
            context["player1_object"] = TgUser.objects.get(
                id=context["player1_object_id"]
            )
        except TgUser.DoesNotExist:
            raise NotFound("TgUser not found.")
        return context

    def get_serializer(
        self, *args, **kwargs
    ) -> TicTacToePropositionPostSerializer | TicTacToePropositionGetSerializer:
        """Returns a serializer for receiving proposals.
        Chooses the serializer based on the action being performed.
        """
        kwargs["context"] = self.get_serializer_context()
        if self.action in ["create", "update"]:
            return TicTacToePropositionPostSerializer(*args, **kwargs)
        elif self.action in ["list", "retrieve"]:
            return TicTacToePropositionGetSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tguser_pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Telegram ID користувача, який створює пропозицію.",
                required=True,
            ),
        ],
        request=TicTacToePropositionPostSerializer,
        description=(
            "Створює нову пропозицію гри в хрестики-нулики для вказаного користувача Telegram. "
            "Користувач автоматично встановлюється як player1."
        ),
        responses={
            201: TicTacToePropositionPostSerializer,
            400: None,
            404: None,
        },
        examples=[
            OpenApiExample(
                name="Успішний запит",
                value={
                    "player1_first": True,
                    "player1_sign": "❌",
                    "player2_sign": "⭕",
                    "expires_at": "2025-06-18T12:00:00Z",
                    "player2_content_type_id": 123,
                    "player2_object_id": 987654321,
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Успішна відповідь",
                value={
                    "id": 1,
                    "player1_first": True,
                    "player1_sign": "❌",
                    "player2_sign": "⭕",
                    "expires_at": "2025-06-18T12:00:00Z",
                    "player2_content_type_id": 123,
                    "player2_object_id": 987654321,
                    "deep_links": {
                        "telegram": "https://t.me/YourBotName?start=proposition_1",
                        "web": "https://yourapp.com/tictactoe/proposition/1",
                    },
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tguser_pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Telegram ID користувача.",
                required=True,
            ),
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID пропозиції.",
                required=True,
            ),
        ],
        description="Деактивує пропозицію гри, встановлюючи is_active=False.",
        responses={
            204: None,
            404: None,
        },
    )
    def destroy(self, request, tguser_pk=None, pk=None):
        """Деактивує пропозицію (is_active = False)."""
        proposition = self.get_object()
        proposition.is_active = False
        proposition.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="tguser_pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Telegram ID користувача.",
                required=True,
            ),
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID пропозиції.",
                required=True,
            ),
        ],
        request=TicTacToePropositionPostSerializer,
        description=(
            "Оновлює існуючу пропозицію гри (PUT або PATCH). "
            "Дозволяє часткове оновлення через PATCH."
        ),
        responses={
            200: TicTacToePropositionPostSerializer,
            400: None,
            404: None,
        },
        examples=[
            OpenApiExample(
                name="Часткове оновлення (PATCH)",
                value={
                    "player2_sign": "⭕",
                    "expires_at": "2025-06-20T12:00:00Z",
                },
                request_only=True,
            ),
        ],
    )
    def update(self, request, tguser_pk=None, pk=None, partial=False):
        """Оновлює пропозицію (PUT або PATCH)."""
        proposition = self.get_object()
        serializer = self.get_serializer(
            proposition, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
