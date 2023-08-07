audit:
	python -m pip_audit

generate-spec:
	python -m scripts.generate_openapi

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
	python -m pytest tests/unit_tests -W ignore::DeprecationWarning
