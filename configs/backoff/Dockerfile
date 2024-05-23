# Dockerfile в configs/backoff/Dockerfile
FROM nginx:1.25.3

# Установим зависимости для Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Создадим виртуальное окружение и установим зависимости
RUN python3 -m venv /opt/venv
COPY configs/backoff/requirements.txt /opt/venv/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /opt/venv/requirements.txt

# Скопируем скрипт проверки из контекста сборки
COPY configs/backoff/check_services.py /usr/bin/check_services.py

# Скопируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY configs /etc/nginx/conf.d

# Обновим CMD для использования виртуального окружения
CMD ["sh", "-c", "/opt/venv/bin/python /usr/bin/check_services.py && nginx -g 'daemon off;'"]
