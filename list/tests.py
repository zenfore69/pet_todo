
import json
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Task, SubTask, TaskImage
from django.urls import reverse
from rest_framework import status
import shutil
from pathlib import Path
from django.conf import settings
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_jpg(filename='test.jpg', size=(100, 100), color=(255, 0, 0)):
    buf = BytesIO()
    img = Image.new('RGB', size, color)
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile(filename, buf.read(), content_type='image/jpeg')

# Create your tests here.
class TaskViewSetTests(APITestCase):

    def tearDown(self):
        # Удаляем всю папку с тестовыми файлами после каждого теста
        if settings.MEDIA_ROOT.exists():
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def setUp(self):
        # Настройка перед каждым тестом
        self.client = APIClient()
        settings.MEDIA_ROOT = Path(settings.BASE_DIR) / 'media' / 'test_trash'
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

        # Создаём тестового пользователя для аутентификации
        self.auth_user = User.objects.create_user(
            username='test_user1',password='pass123'
        )
        self.client.login(username='test_user1', password='pass123')

        # Создаём тестовый объект Task
        self.base_task_data = {
            'name': 'baseTask',
            'description': 'Base Description',
            'status': 'Не начато',
        }
        self.base_task_response = self.client.post(
            reverse('task-list'),
            data=self.base_task_data,
            format='json'
        )
        self.assertEqual(self.base_task_response.status_code, status.HTTP_201_CREATED)
        self.base_task = Task.objects.get(name='baseTask')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.base_task.pk})
        self.list_url = reverse('task-list')

    def test_create_task_with_subtasks_and_image(self):
        subtask_list = [  # Выдели список для удобства
            {
                "name": "testSubtask1",
                "description": "subdesc1",
                "completed": True
            },
            {
                "name": "testSubtask2",
                "description": "subdesc2",
                "completed": False
            }
        ]
        data = {
            "name": "testTask1",
            "description": "testTask1Desc1",
            "status": "В процессе",
            "subtask": json.dumps(subtask_list)
        }

        test_image = create_test_jpg(filename='test_image.jpg')
        files = {'image': test_image}

        response = self.client.post(self.list_url,data=data,files=files, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name='testTask1')
        self.assertEqual(task.description, 'testTask1Desc1')
        self.assertEqual(task.status, "В процессе")
        self.assertEqual(task.creator_username, self.auth_user)
        self.assertEqual(task.subtasks.count(), 2)
        #self.assertEqual(task.taskimage_set.count(),1) починить images
        print(response.data)

