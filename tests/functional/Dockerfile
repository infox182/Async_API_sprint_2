FROM python:3.10

WORKDIR /tests/functional

COPY requirements.txt requirements.txt
COPY __init__.py /tests/__init__.py

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 9001

ENTRYPOINT ["sh", "/tests/functional/start_tests.sh"]
