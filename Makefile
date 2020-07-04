.ONESHELL: all


test:
	@python -m pytest tests/

run:
	@docker-compose up -d

stop:
	@docker-compose down

compile:
	@cd requirements
	@pip-compile requirements.in
	@pip-compile requirements.dev.in

sync:
	@cd requirements
	@pip-sync requirements.txt requirements.dev.txt
