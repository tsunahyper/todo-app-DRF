from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    user = models.ForeignKey(User, related_name='todo', on_delete=models.CASCADE)  # Assuming 'auth.User' is your User model.
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True, null=True)
    completed = models.BooleanField(default=False)

