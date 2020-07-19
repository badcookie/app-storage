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

start-backend:
	@export PYTHONPATH="${PYTHONPATH}:."
	@python server/app.py

start-frontend:
	@cd client
	@npm run start
