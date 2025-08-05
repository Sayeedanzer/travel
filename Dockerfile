# Use official Python slim image
FROM python:3.12-slim

# Prevent .pyc files & buffer issues
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY . .

# Expose port
EXPOSE 8000

# Run Gunicorn (Django wsgi entrypoint)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "travel_expense_app.wsgi.application"]
