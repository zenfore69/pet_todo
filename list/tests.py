from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Task
from django.urls import reverse
from rest_framework import status
import shutil
from pathlib import Path
from django.conf import settings
from datetime import timezone, timedelta
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

    def setUp(self):
        # Настройка перед каждым тестом
        self.client = APIClient()
        settings.MEDIA_ROOT = Path(settings.BASE_DIR) / 'media' / 'test_trash'
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

        # Создаём тестового пользователя для аутентификации
        self.auth_user = User.objects.create_user(
            username='test_user1',password='pass123'
        )
        # Аутентифицируем клиент
        self.client.login(username='test_user1', password='pass123')
        # Создаём тестовый объект Task
        self.task = Task.objects.create(
            name='testTask',
            description='TestDescription 123',
            time_end='2025-09-16T23:35:00+03:00',
            status='Не начато',
            creator_username=self.auth_user,
            image=create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')
        )
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail',kwargs={'pk':self.task.pk})

    def test_create_task(self):
        data =  {
            'name': 'testTask1',
            'description': 'TestDescription 1234',
            'time_end': '2025-09-17T23:35:00+03:00',
            'status': 'В процессе',
            'image': create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(),2)
        self.assertEqual(response.data['name'], 'testTask1')
        self.assertEqual(response.data['description'], 'TestDescription 1234')
        self.assertEqual(response.data['time_end'], '2025-09-17T23:35:00+03:00')
        self.assertEqual(response.data['status'],'В процессе')
        self.assertEqual(response.data['creator_username'],'test_user1')
        self.assertEqual(len(response.data['image']), 67)


    def test_tasks_gets(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

        self.assertEqual(response.data.get('results')[0].get('name'), 'testTask')

    def test_task_detail(self):
        data = {
            'name': 'testTask1',
            'description': 'TestDescription 1234',
            'time_end': '2025-09-17T23:35:00+03:00',
            'status': 'В процессе',
            'image': create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data['name'], 'testTask1')
        self.assertEqual(response.data['description'], 'TestDescription 1234')
        self.assertEqual(response.data['time_end'], '2025-09-17T23:35:00+03:00')
        self.assertEqual(response.data['status'], 'В процессе')
        self.assertEqual(response.data['creator_username'], 'test_user1')
        self.assertEqual(len(response.data['image']), 67)
        response_get_list = self.client.get(self.list_url)
        self.assertEqual(response_get_list.status_code,status.HTTP_200_OK)
        self.assertEqual(response_get_list.data.get('results')[0].get('name'), 'testTask')
        self.assertEqual(response_get_list.data.get('results')[0].get('status'), 'Не начато')



    def test_update_task(self):
        # Тест PUT-запроса (обновление пользователя)
        data = {
            'name': 'updateTask1',
            'description': 'zero',
            'time_end': '2025-09-17T23:35:00+03:00',
            'status': 'В процессе',
            'image': create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')
        }

        response = self.client.put(self.detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'updateTask1')
        self.assertEqual(self.task.description, 'zero')
        self.assertEqual(self.task.time_end.astimezone(timezone(timedelta(hours=3))).isoformat(),'2025-09-17T23:35:00+03:00')
        self.assertEqual(self.task.status,'В процессе')
        self.assertEqual(self.task.creator_username.username, 'test_user1')
        self.assertEqual(len(response.data['image']), 67)



    def test_delete_task(self):
        # Тест DELETE-запроса (удаление пользователя)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)  # Пользователь удалён


    def test_post_status_400(self):
        data = {
            'name': 'testTask1',
            'description': 'TestDescription 1234',
            'time_end': '2025-09-17T23:35:00+03:00',
            'status': 'Не корректное значение',
            'image': create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')

        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_user_unauthenticated(self):
        # Тест POST-запроса без аутентификации
        self.client.logout()  # Выходим из системы
        data = {
            'name': 'updateTask1',
            'description': 'zero',
            'time_end': '2025-09-17T23:35:00+03:00',
            'status': 'В процессе',
            'image': create_test_jpg('ToDo/media/tasks/photo_2023-09-28_23-40-24.jpg')
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

