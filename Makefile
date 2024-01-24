audit:
	python -m pip_audit

generate-spec:
	python -m scripts.generate_openapi

publish-multiple-ci:
	python -m scripts.publish_multiple_ci

integration-tests:
	python -m pytest tests/integration_tests -W ignore::DeprecationWarning

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
	export CI_STORAGE_BUCKET_NAME='$(shell gcloud config get project)' && \
	export PROJECT_NAME='$(shell gcloud config get project)' && \
	coverage run -m pytest -vv ./tests/unit_tests/ -W ignore::DeprecationWarning
	coverage report --omit="./app/repositories/*","./tests/*" --fail-under=90 -m

