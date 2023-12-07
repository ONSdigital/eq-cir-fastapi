FROM python:3.11-alpine

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Install & use pip to install requirements
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./app /code/app

CMD exec uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
