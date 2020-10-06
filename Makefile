.ONESHELL: all

test_file = ''

test:
	@export PYTHONPATH="${PYTHONPATH}:."
	@pytest -s tests/$(test_file)

install:
	@poetry install

setup:
	@cd deploy
	@ansible-playbook -i hosts --limit local setup.yml

server:
	@export PYTHONPATH="${PYTHONPATH}:."
	@python server/main.py

.PHONY: server
