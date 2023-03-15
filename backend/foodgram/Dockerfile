# Start from a Python image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=foodgram.settings

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . /app/

# Скопировать содержимое директории /api_yamdb c локального компьютера
# в директорию /app.
COPY foodgram/ /app

# Выполнить запуск сервера разработки при старте контейнера.
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ] 