.ONESHELL: all

F=tests/

install:
	@poetry install
	@cd client
	@npm install

setup:
	@python setup.py

test:
	@export PYTHONPATH="${PYTHONPATH}:."
	@pytest -s $(F)

server:
	@export PYTHONPATH="${PYTHONPATH}:."
	@python server/app.py

client:
	@cd client
	@npm run start


.PHONY: client server
