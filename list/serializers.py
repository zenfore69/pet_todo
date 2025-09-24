from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task,SubTask
from drf_extra_fields.fields import Base64ImageField

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ["id","name","description","completed"]

class TaskSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator_username.username')
    subtask = SubTaskSerializer(many=True,required=False) #readonly
    image = Base64ImageField()
    class Meta:
        model = Task
        fields = ["id","name","description","time_start","time_end","status","creator_username","image","subtask"]

    def create(self, validated_data):
        task_data =validated_data.pop('subtask',[])
        task = Task.objects.create(**validated_data)

        for data in task_data:
            SubTask.objects.create(task=task,**data)
        return task

    def update(self, instance, validated_data):
        task_data = validated_data.pop('subtask', [])
        instance = super().update(instance,validated_data)

        if task_data is not None:
             instance.subtask.all().delete()

             for data in task_data:
                 SubTask.objects.create(task=instance, **data)
        return instance

class UserSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id','username','tasks']