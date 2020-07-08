.ONESHELL: all


test:
	@export PYTHONPATH=.
	@pytest -s

install:
	@poetry install

setup:
	@cd deploy
	@ansible-playbook -i hosts local_setup.yml
