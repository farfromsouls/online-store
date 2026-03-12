import os
import random
import django
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Product, Review 
User = get_user_model()
fake = Faker('ru_RU') 

def clear_data():
    Review.objects.all().delete()
    Product.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

def create_users(count=5):
    users = []
    for _ in range(count):
        username = fake.user_name()
        while User.objects.filter(username=username).exists():
            username = fake.user_name()
        user = User.objects.create_user(
            username=username,
            email=fake.email(),
            password='testpass123' 
        )
        users.append(user)
    print(f'Создано {len(users)} пользователей.')
    return users

def create_products(count=10):
    products = []
    
    available_images = [
        'products/noimg.jpg',  
    ]
    
    for i in range(count):
        name = fake.word().capitalize() + ' ' + fake.word().capitalize()
        name = name[:40]
        
        product = Product.objects.create(
            Name=name,
            Image=random.choice(available_images),
            Cost=random.randint(50, 500000),
            Amount=random.randint(0, 100),
            Available=random.choice([True, False]),
            Description=fake.text(max_nb_chars=200),
            Rating=-1,        
            ReviewCount=0
        )
        products.append(product)
        
    print(f'Создано {len(products)} продуктов.')
    return products

def create_reviews(products, users, count):
    reviews_created = 0
    for _ in range(count):
        product = random.choice(products)
        author = random.choice(users)
        rating = random.randint(1, 5)
        text = fake.sentence(nb_words=10) if random.random() > 0.3 else ""  
        
        Review.objects.create(
            Product=product,
            Author=author,
            Text=text,
            Rating=rating
        )
        reviews_created += 1
    print(f'Создано {reviews_created} отзывов.')

def main():
    print("Начинаем заполнение базы тестовыми данными...")
    clear_data() 
    users = create_users(int(input("Кол-во юзеров: ")))
    products = create_products(int(input("Кол-во продуктов: ")))
    create_reviews(products, users, int(input("Кол-во отзывов: ")))
    print("Готово!")

if __name__ == '__main__':
    main()