from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import NotAcceptable

from .models import Task, SubTask, TaskImage, status_choices
from django.forms import ImageField as DjangoImageField

class TaskImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskImage
        fields = ["id", "image", "task"]
        extra_kwargs = {
            'task': {'required': False}
        }

    def validate(self, attrs):
        default_error_messages = {
            'invalid_image': 'Upload a valid image. The file you uploaded was either not an image or a corrupted image.',
        }
        for i in self.initial_data.getlist('image'):
            django_field = DjangoImageField()
            django_field.error_messages = default_error_messages
            django_field.clean(i)
        return attrs

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ["id", "name", "description", "completed"]

class TaskSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator_username.username')
    subtask = SubTaskSerializer(source='subtasks', allow_null=True, many=True, required=False)
    taskimage = TaskImageSerializer(source='taskimage_set', allow_null=True, many=True, required=False)

    class Meta:
        model = Task
        fields = ["id", "name", "description", "time_start", "time_end", "status", "creator_username",
                  "subtask", "taskimage"]

    def create(self, validated_data):
        # Pop по имени source (subtasks), а не по имени поля сериализатора (subtask)
        subtask_data = validated_data.pop('subtasks', None)

        validated_data.pop('image', None)  # Удаляем 'image' из data, если оно там

        try:
            task_obj = Task.objects.create(**validated_data)
        except Exception as e:
            raise NotAcceptable(detail={'message': 'The request is not acceptable.', 'error': str(e)}, code=406)

        # Изображения (как раньше, работает по отладке)
        if "included_images" in self.context:
            images_data = self.context['included_images']
            image_list = images_data.getlist('image')
            for img in image_list:
                TaskImage.objects.create(image=img, task=task_obj)

        # Подзадачи (создаём и добавляем через add)
        if subtask_data:
            for sub_data in subtask_data:
                subtask_obj = SubTask.objects.create(
                    name=sub_data.get('name', ''),
                    description=sub_data.get('description', None),
                    completed=sub_data.get('completed', False)
                )
                task_obj.subtasks.add(subtask_obj)

        return task_obj

    def update(self, instance, validated_data):
        # Аналогично pop по source
        subtask_data = validated_data.pop('subtasks', None)
        validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if subtask_data is not None:
            instance.subtasks.clear()  # Лучше clear() вместо delete(), чтобы не удалять подзадачи навсегда (если они используются где-то ещё)
            for sub_data in subtask_data:
                subtask_obj = SubTask.objects.create(
                    name=sub_data.get('name', ''),
                    description=sub_data.get('description', None),
                    completed=sub_data.get('completed', False)
                )
                instance.subtasks.add(subtask_obj)

        if "included_images" in self.context:
            instance.taskimage_set.all().delete()  # Удаляем старые изображения
            images_data = self.context['included_images']
            image_list = images_data.getlist('image')
            for img in image_list:
                TaskImage.objects.create(image=img, task=instance)
        # Если нужно обновлять изображения при PUT/PATCH, добавьте логику здесь (например, удалить старые и добавить новые из FILES)
        return instance

class UserSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'tasks']