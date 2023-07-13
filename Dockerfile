FROM python:3.11

WORKDIR /code

# Install & use pipenv to install requirements
COPY Pipfile Pipfile.lock ./code/
ARG PIPENV_PIPFILE=./code/Pipfile

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

COPY ./app /code/app

CMD exec uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
