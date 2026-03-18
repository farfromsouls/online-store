from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

from django_redis import get_redis_connection 

from user.models import CustomUser

import json 
import os

REDIS_TTL = os.environ.get("REDIS_TTL")

class Product(models.Model):
    Name = models.TextField(max_length=40)
    Image = models.ImageField(upload_to='products/', default='products/noimg.jpg', null=True)
    Cost = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(500000)])
    Amount = models.IntegerField(default=0)
    Available = models.BooleanField()
    Description = models.TextField(default="Описание отсутствует", max_length=1000)
    Rating = models.FloatField(default=-1)
    ReviewCount = models.IntegerField(default=0)
    
    def __str__(self):
        return self.Name
    
    def update_rating(self, new_rating):
        if self.ReviewCount == 0 or self.Rating == -1:
            self.Rating = new_rating
        else:
            total_sum = self.Rating * self.ReviewCount + new_rating
            self.Rating = round(total_sum / (self.ReviewCount + 1), 2)
        self.ReviewCount += 1
        self.save()
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            if self.Amount > 0:
                self.Available = True
            else:
                self.Available = False
        super().save(*args, **kwargs)

        try:
            key = f"product_{self.id}"
            redis_conn = get_redis_connection('default')
            product_dict = model_to_dict(self)
            
            if self.Image:
                product_dict['Image'] = self.Image.url
            else:
                product_dict['Image'] = None

            data = {"product": product_dict, "reviews": []}
            redis_conn.setex(key, REDIS_TTL, json.dumps(data, cls=DjangoJSONEncoder))
        except Exception as e:
            print(f"Redis cache error: {e}")
        
    def get_image_url(self):
        if self.Image:
            return self.Image.url
        return ''
    
    def to_dict(self):
        data = {
            'id': self.id,
            'Name': self.Name,
            'Image': self.Image.url if self.Image else None,
            'Cost': self.Cost,
            'Amount': self.Amount,
            'Available': self.Available,
            'Description': self.Description,
            'Rating': self.Rating,
            'ReviewCount': self.ReviewCount
        }
        return data
    
class Review(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Text = models.TextField(default="", max_length=1000)
    Rating = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.Product.update_rating(self.Rating)
        super().save(*args, **kwargs)
            
    def __str__(self):
            return f"{self.Author.username}: {self.Product}"