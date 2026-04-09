# online-store 🛍️

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-darkgreen?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8-green?style=for-the-badge&logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![Nginx](https://img.shields.io/badge/Nginx-1.25-green?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Aiogram](https://img.shields.io/badge/aiogram-3.x-blue?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.aiogram.dev)

## 🚀 Starting
Make sure you have Docker installed.

1) Create a .env file in the main directory with the following content:

    ```dotenv
    DB_NAME=onlinestore
    DB_USER=postgres
    DB_PASSWORD=yourpassword
    DB_HOST=db
    DB_PORT=5432

    DEBUG=True
    DJANGO_SECRET_KEY=your-secret-key-here

    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_TTL=300

    ELASTICSEARCH_HOST=elasticsearch
    ELASTICSEARCH_PORT=9200

    BOT_TOKEN=your-bot-token
    ```

2. Use these Makefile commands in the project directory.

## ⚙️ Makefile Commands

| Command | Description |
|---------|-------------|
| `make up-b` | Build images and start all containers |
| `make up` | Start containers (without rebuilding) |
| `make down` | Stop all containers |
| `make down-v` | Stop containers and remove volumes (clears PostgreSQL, Redis, static files) |
| `make rmi` | Remove all Docker images |
| `make fill-db` | Populate PostgreSQL with test data using Faker |
| `make admin` | Create Django superuser |

## 🎯 API Endpoints 

**Only admin users are permitted**

    product/<int:id>/ - GET, PUT, PATCH, DELETE
    products/         - GET, POST

## ✈️ Telegram Bot

**You must be logged in as an admin**

You will receive notifications when someone buys products from your site.

**Menu:**
 - Add a new product
 - Change product properties
 - Delete a product
 - Get the list of all products

