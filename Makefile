.ONESHELL: all

test_file = ''

test:
	@export PYTHONPATH="${PYTHONPATH}:."
	@pytest -s tests/$(test_file)

install:
	@poetry install
	@cd client
	@yarn install

setup:
	@cd deploy
	@ansible-playbook -i hosts local_setup.yml

server:
	@export PYTHONPATH="${PYTHONPATH}:."
	@python server/main.py

client:
	@cd client
	@yarn start


.PHONY: client server
