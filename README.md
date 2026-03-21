# online store

## Starting
1) Create .env in main directory with:

```dotenv
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=db
DB_PORT=5432

DJANGO_SECRET_KEY=
DEBUG=

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_TTL=300

ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
```

2. Check Makefile to build and run.