FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dashboard.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copy application files
COPY dashboard_server.py .
COPY dashboard/ ./dashboard/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "dashboard_server.py"]