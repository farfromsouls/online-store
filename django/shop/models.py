from django.db import models


class Product(models.Model):
    Name = models.TextField()
    Image = models.ImageField(upload_to='products/', null=True, blank=True)
    Cost = models.IntegerField()
    Description = models.TextField()
    Rating = models.IntegerField()