# Global Variables
GOOGLE_APPLICATION_CREDENTIALS=sandbox-key.json
PROJECT_ID = $(shell gcloud config get project)
OAUTH_BRAND_NAME = $(shell gcloud iap oauth-brands list --format='value(name)' --limit=1 --project=$(PROJECT_ID))
OAUTH_CLIENT_NAME = $(shell gcloud iap oauth-clients list $(OAUTH_BRAND_NAME) --format='value(name)' \
        --limit=1)
OAUTH_CLIENT_ID = $(shell echo $(OAUTH_CLIENT_NAME)| cut -d'/' -f 6)
SANDBOX_IP_ADDRESS = $(shell gcloud compute addresses list --global  --filter=name:$(PROJECT_ID)-cir-static-lb-ip --format='value(address)' --limit=1 --project=$(PROJECT_ID))

start-cloud-dev:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 3030

unit-tests:
	export CONF=unit && \
	export CI_STORAGE_BUCKET_NAME='the-ci-schema-bucket' && \
	export PROJECT_ID='$(PROJECT_ID)' && \
	poetry run pytest --cov=app --cov-fail-under=90 --cov-report term-missing --cov-config=.coveragerc_unit -vv ./tests/unit_tests/ -W ignore::DeprecationWarning

integration-tests-sandbox:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	export DEFAULT_HOSTNAME=${SANDBOX_IP_ADDRESS}.nip.io && \
	export URL_SCHEME='https' && \
	export OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} && \
	export PYTHONPATH=app && \
	poetry run pytest tests/integration_tests -vv -W ignore::DeprecationWarning

#For use only by automated cloudbuild, is not intended to work locally.
integration-tests-cloudbuild:
	export PROJECT_ID=${INT_PROJECT_ID} && \
	export FIRESTORE_DB_NAME=${INT_FIRESTORE_DB_NAME} \
	export CI_STORAGE_BUCKET_NAME=${INT_CI_STORAGE_BUCKET_NAME} && \
	export DEFAULT_HOSTNAME=${INT_DEFAULT_HOSTNAME} && \
	export URL_SCHEME=${INT_URL_SCHEME} && \
	export OAUTH_CLIENT_ID=${INT_OAUTH_CLIENT_ID} && \
	export PYTHONPATH=app && \
	python -m pytest tests/integration_tests -vv -W ignore::DeprecationWarning

generate-spec:
	export PROJECT_ID='$(PROJECT_ID)' && \
	export FIRESTORE_DB_NAME='$(PROJECT_ID)-cir' && \
	export CI_STORAGE_BUCKET_NAME='$(PROJECT_ID)-cir-europe-west2-schema' && \
	export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} && \
	python -m scripts.generate_openapi

publish-multiple-ci:
	python -m scripts.publish_multiple_ci


.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf megalinter-reports

.PHONY: format
format:  ## Format the code.
	poetry run black .
	poetry run ruff check . --fix

.PHONY: poetry-lint
poetry-lint:  ## Run all linters (black/ruff/pylint/mypy).
	poetry run black --check .
	poetry run ruff check .
	make mypy

.PHONY: test
test:  ## Run the tests and check coverage.
    export CONF=unit && \
    export CI_STORAGE_BUCKET_NAME='the-ci-schema-bucket' && \
    export PROJECT_ID='$(PROJECT_ID)' && \
	poetry run pytest --cov=app --cov-fail-under=90 --cov-report term-missing --cov-config=.coveragerc_unit -vv ./tests/unit_tests/ -W ignore::DeprecationWarning


.PHONY: mypy
mypy:  ## Run mypy.
	poetry run mypy app

.PHONY: install
install:  ## Install the dependencies excluding dev.
	poetry install --only main --no-root

.PHONY: install-dev
install-dev:  ## Install the dependencies including dev.
	poetry install --no-root

.PHONY: megalint
megalint:  ## Run the mega-linter.
	docker run --platform linux/amd64 --rm \
		-v /var/run/docker.sock:/var/run/docker.sock:rw \
		-v $(shell pwd):/tmp/lint:rw \
		oxsecurity/megalinter:v7
