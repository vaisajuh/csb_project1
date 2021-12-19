from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()