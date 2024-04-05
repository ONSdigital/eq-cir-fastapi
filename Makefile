GOOGLE_APPLICATION_CREDENTIALS=sandbox-key.json
PROJECT_ID = $(shell gcloud config get project)

audit:
	python -m pip_audit

generate-spec:
	python -m scripts.generate_openapi

publish-multiple-ci:
	python -m scripts.publish_multiple_ci

integration-tests-sandbox:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	export DEFAULT_HOSTNAME='34.111.178.226.nip.io' && \
	export URL_SCHEME='https' && \
	export OAUTH_CLIENT_ID='949511058357-tnn536t91kd7omqihao2hpbs3h44c3sm.apps.googleusercontent.com' && \
	export PYTHONPATH=app && \
	python -m pytest tests/integration_tests -vv -W ignore::DeprecationWarning

integration-tests:
	python -m pytest --cov=app tests/integration_tests -W ignore::DeprecationWarning

lint:
	python -m black --line-length 127 .
	python -m flake8 --max-line-length=127 --exclude=./scripts,env
	python -m mypy . --exclude env --disable-error-code attr-defined --disable-error-code import
	python -m isort . --profile black --skip env

lint-check:
	python -m black . --check --line-length 127
	python -m flake8 --max-line-length=127 --exclude=./scripts,env
	python -m mypy . --exclude env --disable-error-code attr-defined --disable-error-code import
	python -m isort . --check-only --profile black --skip env

unit-tests:
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export PROJECT_ID='$(PROJECT_ID)' && \
	python -m pytest --cov=app --cov-fail-under=90 --cov-report term-missing --cov-config=.coveragerc_unit -vv ./tests/unit_tests/ -W ignore::DeprecationWarning

start-cloud-dev:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3030
