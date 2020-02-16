test:
	@python -m pytest src/tests/

run:
	@docker-compose up -d

stop:
	@docker-compose down
