from django.db import models

status_choices = (
    ('Не начато', 'Не начато'),
    ('В процессе', 'В процессе'),
    ('Завершенно', 'Завершено'),
)

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000,blank=True,null=True)
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=30,choices=status_choices)
    image = models.ImageField(upload_to='tasks/',null=True)
    creator_username = models.ForeignKey('auth.User',related_name="tasks",on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["time_start"]

class SubTask(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000,blank=True,null=True)
    completed = models.BooleanField(default=False)
    task = models.ForeignKey(Task,related_name="subtask", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
