include .env

up:
	docker-compose up

up-b:
	docker-compose up --build

down:
	docker-compose down

down-v:
	docker-compose down -v

rmi:
	docker image prune -a -f

fill-db:
	docker exec -it django_app python test_populate_db.py

admin:
	docker exec -it django_app python manage.py createsuperuser