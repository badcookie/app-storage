.ONESHELL: all

F=tests/

install:
	@poetry install
	@cd client
	@npm install

setup:
	@cd deploy
	@ansible-playbook -i hosts local_setup.yml

test:
	@export PYTHONPATH=.
	@pytest -s $(F)

start-backend:
	@export PYTHONPATH=.
	@python server/app.py
