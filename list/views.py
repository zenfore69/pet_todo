from logging import raiseExceptions
from django.utils.autoreload import raise_last_exception
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import NotAcceptable
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Task, TaskImage, SubTask
from .parser import MultipartJsonParser
from .permissions import IsOwnerOrReadOnly
from .serializers import TaskSerializer, UserSerializer, SubTaskSerializer,TaskImageSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status


class TaskViewSet(viewsets.ModelViewSet):
    parser_classes = [MultipartJsonParser,JSONParser]
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

    def get_serializer_context(self):
        context = super(TaskViewSet,self).get_serializer_context()

        if len(self.request.FILES) > 0:
            context.update({
                'included_images': self.request.FILES
            })
        return context

    def create(self, request, *args, **kwargs):
        try:
            image_serializer = TaskImageSerializer(data=request.FILES)
            image_serializer.is_valid(raise_exception=True)
        except Exception:
            raise NotAcceptable(detail={'message': 'Invalid image.'}, code=406)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TaskImageViewSet(viewsets.ModelViewSet):
    queryset = TaskImage
    serializer_class = TaskImageSerializer

class SubTaskViewSet(viewsets.ModelViewSet):
    queryset = SubTask
    serializer_class = SubTaskSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer