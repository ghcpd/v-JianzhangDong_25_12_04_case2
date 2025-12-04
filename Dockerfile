FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY inputs.py .
COPY inputs_backup.py .
COPY auto_test.py .
COPY run_test.sh .
COPY report.json .

# Create necessary directories
RUN mkdir -p /app/logs /app/configs

# Set environment variables
ENV FLASK_APP=inputs.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Make run_test.sh executable
RUN chmod +x run_test.sh

# Default command
CMD ["/bin/bash"]
