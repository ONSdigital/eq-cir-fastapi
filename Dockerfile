FROM python:3.11-slim-bullseye

WORKDIR /code

# Install & use pip to install requirements
RUN python -m pip install --upgrade pip
RUN pip install -r requirements/production.txt

COPY ./app /code/app

CMD exec uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
