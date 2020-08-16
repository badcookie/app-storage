.ONESHELL: all

F=tests/

install:
	@poetry install
	@cd client
	@yarn install

setup:
	@python setup.py

test:
	@export PYTHONPATH="${PYTHONPATH}:."
	@pytest -s $(F)

server:
	@export PYTHONPATH="${PYTHONPATH}:."
	@python server/main.py

client:
	@cd client
	@npm run start


.PHONY: client server
