from pydoc import describe

from rest_framework import permissions
from rest_framework import viewsets
from .models import Task
from .permissions import IsOwnerOrReadOnly
from .serializers import TaskSerializer,UserSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator_username = self.request.user)

    def get_queryset(self):
        queryset = Task.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        return queryset



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer