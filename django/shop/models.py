from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import CustomUser

class Product(models.Model):
    Name = models.TextField(max_length=40)
    Image = models.ImageField(upload_to='products/', default='products/noimg.jpg', null=True)
    Cost = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(500000)])
    Amount = models.IntegerField(default=0)
    Available = models.BooleanField(default=True)
    Description = models.TextField(default="", max_length=1000)
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
    
class Review(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    Author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Text = models.TextField(default="", max_length=1000)
    Rating = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.Product.update_rating(self.Rating)
            
    def __str__(self):
            return f"{self.Author.username}: {self.Product}"