from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from user_management.models import TgUser
from .models import TicTacToeProposition
from .serializers import TicTacToePropositionGetSerializer, TicTacToePropositionFilterSerializer, \
    TicTacToePropositionPostSerializer


class TicTacToePropositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управління пропозиціями гри в хрестики-нулики для користувачів Telegram.
    Дозволяє створювати, отримувати, оновлювати та деактивувати пропозиції.
    """

    @extend_schema(
        parameters=[
            TicTacToePropositionFilterSerializer,
            OpenApiParameter(
                name='tguser_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Telegram ID користувача, для якого повертаються пропозиції.',
                required=True,
            ),
        ],
        description=(
                'Повертає список активних пропозицій гри в хрестики-нулики для вказаного користувача Telegram. '
                'Підтримує фільтрацію за статусом, роллю гравця та терміном дії.'
        ),
        responses={
            200: TicTacToePropositionGetSerializer(many=True),
            404: None,
        },
        examples=[
            OpenApiExample(
                name='Успішна відповідь',
                value=[
                    {
                        'id': 1,
                        'player1': {'id': 12345678, 'first_name': 'John', 'last_name': None, 'username': '@john'},
                        'player2': None,
                        'player1_first': True,
                        'player1_sign': '❌',
                        'player2_sign': '⭕',
                        'created_at': '2025-06-11T15:00:00Z',
                        'accepted_at': None,
                        'status': 'incomplete',
                        'expires_at': '2025-06-18T12:00:00Z',
                        'deep_links': {
                            'telegram': 'https://t.me/YourBotName?start=proposition_1',
                            'web': 'https://yourapp.com/tictactoe/proposition/1'
                        }
                    }
                ],
                response_only=True,
                status_codes=['200'],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tguser_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Telegram ID користувача.',
                required=True,
            ),
            OpenApiParameter(
                name='pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID пропозиції.',
                required=True,
            ),
        ],
        description='Повертає деталі конкретної активної пропозиції для вказаного користувача.',
        responses={
            200: TicTacToePropositionGetSerializer,
            404: None,
        },
        examples=[
            OpenApiExample(
                name='Успішна відповідь',
                value={
                    'id': 1,
                    'player1': {'id': 12345678, 'first_name': 'John', 'last_name': None, 'username': '@john'},
                    'player2': None,
                    'player1_first': True,
                    'player1_sign': '❌',
                    'player2_sign': '⭕',
                    'created_at': '2025-06-11T15:00:00Z',
                    'accepted_at': None,
                    'status': 'pending',
                    'expires_at': '2025-06-18T12:00:00Z',
                    'deep_links': {
                        'telegram': 'https://t.me/YourBotName?start=proposition_1',
                        'web': 'https://yourapp.com/tictactoe/proposition/1'
                    }
                },
                response_only=True,
                status_codes=['200'],
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tguser_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Telegram ID користувача, який створює пропозицію.',
                required=True,
            ),
        ],
        request=TicTacToePropositionPostSerializer,
        description=(
                'Створює нову пропозицію гри в хрестики-нулики для вказаного користувача Telegram. '
                'Користувач автоматично встановлюється як player1.'
        ),
        responses={
            201: TicTacToePropositionPostSerializer,
            400: None,
            404: None,
        },
        examples=[
            OpenApiExample(
                name='Успішний запит',
                value={
                    'player1_first': True,
                    'player1_sign': '❌',
                    'player2_sign': '⭕',
                    'expires_at': '2025-06-18T12:00:00Z',
                    'player2_content_type_id': 123,
                    'player2_object_id': 987654321,
                },
                request_only=True,
            ),
            OpenApiExample(
                name='Успішна відповідь',
                value={
                    'id': 1,
                    'player1_first': True,
                    'player1_sign': '❌',
                    'player2_sign': '⭕',
                    'expires_at': '2025-06-18T12:00:00Z',
                    'player2_content_type_id': 123,
                    'player2_object_id': 987654321,
                    'deep_links': {
                        'telegram': 'https://t.me/YourBotName?start=proposition_1',
                        'web': 'https://yourapp.com/tictactoe/proposition/1'
                    }
                },
                response_only=True,
                status_codes=['201'],
            ),
        ]
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
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tguser_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Telegram ID користувача.',
                required=True,
            ),
            OpenApiParameter(
                name='pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID пропозиції.',
                required=True,
            ),
        ],
        description='Деактивує пропозицію гри, встановлюючи is_active=False.',
        responses={
            204: None,
            404: None,
        }
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
                name='tguser_pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='Telegram ID користувача.',
                required=True,
            ),
            OpenApiParameter(
                name='pk',
                type=int,
                location=OpenApiParameter.PATH,
                description='ID пропозиції.',
                required=True,
            ),
        ],
        request=TicTacToePropositionPostSerializer,
        description=(
                'Оновлює існуючу пропозицію гри (PUT або PATCH). '
                'Дозволяє часткове оновлення через PATCH.'
        ),
        responses={
            200: TicTacToePropositionPostSerializer,
            400: None,
            404: None,
        },
        examples=[
            OpenApiExample(
                name='Часткове оновлення (PATCH)',
                value={
                    'player2_sign': '⭕',
                    'expires_at': '2025-06-20T12:00:00Z',
                },
                request_only=True,
            ),
        ]
    )
    def update(self, request, tguser_pk=None, pk=None, partial=False):
        """Оновлює пропозицію (PUT або PATCH)."""
        proposition = self.get_object()
        serializer = self.get_serializer(proposition, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
