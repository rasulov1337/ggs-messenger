# Используем официальный Python образ в качестве базового
FROM python:3.10

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем и обновляем pip
RUN pip install --upgrade pip

# Устанавливаем зависимости для проекта
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Открываем порты
EXPOSE 8000 8010

RUN python manage.py migrate

# Команда для запуска приложения
#CMD ["gunicorn", "-c", "configs/gunicorn.conf.py", "msgr.wsgi"]
# RUN centrifugo --config=configs/centrifugo.json
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
