FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dashboard.txt .
COPY requirements-selfbot.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dashboard.txt && \
    pip install --no-cache-dir -r requirements-selfbot.txt

# Copy application files
COPY dashboard_server.py .
COPY selfbot.py .
COPY dashboard/ ./dashboard/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run both the dashboard server and selfbot
CMD python dashboard_server.py & python selfbot.py