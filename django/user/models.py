from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    Bucket = models.JSONField(default=dict)

    def __str__(self):
        return self.username