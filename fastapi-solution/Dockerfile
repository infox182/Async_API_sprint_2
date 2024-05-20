FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY ./src .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "main:app", "--workers", "4", "--worker-class", \
            "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
