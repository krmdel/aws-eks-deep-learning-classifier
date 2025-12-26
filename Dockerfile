FROM python:3.13.5-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-pipfile

COPY app.py clothing-model.onnx ./

EXPOSE 8080

ENTRYPOINT ["pipenv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]