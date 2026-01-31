# Use official Python 3.12 slim image
FROM python:3.12-slim
 
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1
 
# Set working directory
WORKDIR /app
 
# Install system dependencies
RUN apt-get update && apt-get install -y \
   build-essential \
  default-libmysqlclient-dev \
   pkg-config \
   libpq-dev \
   curl \
   && rm -rf /var/lib/apt/lists/*
 
# Install pipenv or requirements.txt dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
   && pip install -r requirements.txt
 
# Copy project files
COPY . .
 
EXPOSE 8013
 
# Run the Django app using Daphne (ASGI server for WebSocket support)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8013", "project.asgi:application"]

