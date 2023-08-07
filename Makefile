audit:
	pipenv run pip-audit

cloudbuild-install:
	python -m pip install pipenv
	python -m pipenv install --dev --system --deploy

generate-spec:
	python -m scripts.generate_openapi

lint:
	pipenv run black --line-length 127 .
	pipenv run flake8 --max-line-length=127 --exclude=./scripts,venv
	pipenv run mypy . --exclude venv --disable-error-code attr-defined --disable-error-code import
	pipenv run isort . --profile black

lint-check:
	pipenv run black . --check --line-length 127
	pipenv run flake8 --max-line-length=127 --exclude=./scripts,venv
	pipenv run mypy . --exclude venv --disable-error-code attr-defined --disable-error-code import
	pipenv run isort . --check-only --profile black

unit-tests:
	export CI_STORAGE_BUCKET_NAME='$(shell gcloud config get project)' && \
	export PROJECT_NAME='$(shell gcloud config get project)' && \
	pipenv run pytest tests/unit_tests -W ignore::DeprecationWarning
