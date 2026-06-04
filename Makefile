up:
	docker-compose up --build

down:
	docker-compose down

reset:
	docker-compose down -v

logs:
	docker-compose logs -f

seed:
	docker-compose run --rm seed-job

rebuild:
	docker-compose down
	docker-compose up --build