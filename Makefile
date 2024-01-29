# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

isort:
	@isort --profile black --filter-files
	
black:
	@black --check `find . -name "*.py" | grep -v "alembic/versions"`

check_code:
	@flake8 --ignore=E501,W503 `find . -name "*.py" | grep -v "alembic/versions"`
	@pylint --min-similarity-lines 81 `find . -name "*.py" | grep -v "alembic/versions"`

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

pre-commit:
	@pre-commit run --file `find . -name "*.py" | grep -v "alembic"`
	@pre-commit run check-yaml --file `find . -name "*.y*ml"`

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr use_cases_calc-*.dist-info
	@rm -fr use_cases_calc.egg-info

install:
	@pip install . -U

all: clean install test check_code

run_api:
	uvicorn api.fast:app --host 0.0.0.0 --port 8081 --env-file .env.development --ssl-certfile ./localhost.pem --ssl-keyfile ./localhost-key.pem  --reload
