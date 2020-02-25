test:
	@python3 -m pytest tests/

run:
	@docker-compose up -d

stop:
	@docker-compose down
