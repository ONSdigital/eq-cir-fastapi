# Global Variables
GOOGLE_APPLICATION_CREDENTIALS=sandbox-key.json
PROJECT_ID = $(shell gcloud config get project)
OAUTH_BRAND_NAME = $(shell gcloud iap oauth-brands list --format='value(name)' --limit=1 --project=$(PROJECT_ID))
OAUTH_CLIENT_NAME = $(shell gcloud iap oauth-clients list $(OAUTH_BRAND_NAME) --format='value(name)' \
        --limit=1)
OAUTH_CLIENT_ID = $(shell echo $(OAUTH_CLIENT_NAME)| cut -d'/' -f 6)
SANDBOX_IP_ADDRESS = $(shell gcloud compute addresses list --global  --filter=name:$(PROJECT_ID)-cir-static-lb-ip --format='value(address)' --limit=1 --project=$(PROJECT_ID))

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
	export DEFAULT_HOSTNAME=${SANDBOX_IP_ADDRESS}.nip.io && \
	export URL_SCHEME='https' && \
	export OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} && \
	export PYTHONPATH=app && \
	python -m pytest tests/integration_tests -vv -W ignore::DeprecationWarning

integration-tests-cloudbuild:
	export PROJECT_ID=${INT_PROJECT_ID} && \
	export FIRESTORE_DB_NAME=${INT_FIRESTORE_DB_NAME} \
	export CI_STORAGE_BUCKET_NAME=${INT_CI_STORAGE_BUCKET_NAME} && \
	export DEFAULT_HOSTNAME=${INT_DEFAULT_HOSTNAME} && \
	export URL_SCHEME=${INT_URL_SCHEME} && \
	export OAUTH_CLIENT_ID=${INT_OAUTH_CLIENT_ID} && \
	export PYTHONPATH=app && \
	python -m pytest tests/integration_tests -vv -W ignore::DeprecationWarning

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

lint-fix:
	black . --line-length 127

unit-tests:
	export CI_STORAGE_BUCKET_NAME='the-ci-schema-bucket' && \
	export PROJECT_ID='$(PROJECT_ID)' && \
	python -m pytest --cov=app --cov-fail-under=90 --cov-report term-missing --cov-config=.coveragerc_unit -vv ./tests/unit_tests/ -W ignore::DeprecationWarning

start-cloud-dev:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3030

