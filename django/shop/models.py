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
    
    @property
    def image_url(self):
        if hasattr(self.Image, 'url'):
            return self.Image.url
        return self.Image
    
    @property
    def stars(self):
        full_stars = round(self.Rating)
        return full_stars*"★" + (5-full_stars)*"☆" 
    
    @property
    def rating_color(self):
        rating = float(self.Rating) if self.Rating else 0
        
        if rating >= 4.5:
            return "#ddd31d"
        elif rating >= 4.0:
            return "#c9c41a"
        elif rating >= 3.5:
            return "#d4903c"
        elif rating >= 3.0:
            return "#ff8c00"
        elif rating >= 2.5:
            return "#ff6b00"
        elif rating >= 2.0:
            return "#ff4500"
        else:
            return "#ff0000"
    
    def update_rating(self, new_rating):
        if self.ReviewCount == 0 or self.Rating == -1:
            self.Rating = new_rating
        else:
            total_sum = self.Rating * self.ReviewCount + new_rating
            self.Rating = round(total_sum / (self.ReviewCount + 1), 2)
        self.ReviewCount += 1
        self.save()
        
    def update_amount(self, minus_val):
        self.Amount = self.Amount - minus_val
        self.save()
        
    def save(self, *args, **kwargs):
        redis_conn = get_redis_connection('default')
        
        if self.Amount > 0:
            self.Available = True
            key = f"product_{self.id}"
            product_dict = model_to_dict(self)
            
            if self.Image:
                product_dict['Image'] = self.Image.url
            else:
                product_dict['Image'] = None

            data = {"product": product_dict, "reviews": []}
            redis_conn.setex(key, REDIS_TTL, json.dumps(data, cls=DjangoJSONEncoder))
        else:
            redis_conn.delete(f"product_{self.id}")
            
            first_by_rating_key = 'first_by_rating'
            cached_data = redis_conn.get(first_by_rating_key)
            
            if cached_data:
                first_by_rating = json.loads(cached_data)
                if isinstance(first_by_rating, list) and self.id in first_by_rating:
                    first_by_rating.remove(self.id)
                    redis_conn.setex(first_by_rating_key, REDIS_TTL, json.dumps(first_by_rating))
            
            self.Available = False
        
        super().save(*args, **kwargs)

        
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