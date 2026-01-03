FROM python:3.13-slim

WORKDIR /app

# Копируем requirements для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Запускаем приложение
CMD ["python", "-m", "src.main"]