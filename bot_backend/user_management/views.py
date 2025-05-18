from rest_framework import viewsets

from .models import TgUser
from .serializers import TgUserSerializer


class TgUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer
    
