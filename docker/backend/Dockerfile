FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY ./requirements/base.txt /app/requirements/base.txt
COPY ./requirements/prod.txt /app/requirements/prod.txt
RUN pip install --upgrade pip && pip install -r requirements/prod.txt

# Copy project files
COPY . /app/

# Copy entrypoint script
COPY ../docker/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run entrypoint
ENTRYPOINT ["/entrypoint.sh"]
