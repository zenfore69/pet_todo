from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator_username.username')
    class Meta:
        model = Task
        fields = ["id","name","description","time_start","time_end","status","creator_username","image"]

class UserSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id','username','tasks']