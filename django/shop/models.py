from django.db import models


class Book(models.Model):
    title = models.TextField()
    