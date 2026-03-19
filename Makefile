include .env

up:
	docker-compose up --build
down:
	docker-compose down
downv:
	docker-compose down -v