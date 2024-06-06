# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /code

# Копируем файл requirements.txt в рабочую директорию
COPY requirements.txt /code/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все содержимое проекта в рабочую директорию
COPY . /code/

# Указываем команду для запуска сервера Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
