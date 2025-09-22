from django.urls import path,include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet,TaskViewSet


router =  DefaultRouter()
router.register(r'tasks', TaskViewSet,basename='task')
router.register(r'users',UserViewSet,basename='user')
urlpatterns = [
    path('',include(router.urls))
]