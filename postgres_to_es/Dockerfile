FROM python:3.12

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY ./app .

EXPOSE 9000

ENTRYPOINT ["python3", "main.py"]