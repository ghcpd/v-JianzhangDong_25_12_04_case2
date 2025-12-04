FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY inputs.py .
COPY inputs_backup.py .

# Create necessary directories
RUN mkdir -p config logs

# Set environment variables (these should be overridden at runtime)
ENV PAYMENT_TOKEN=""
ENV MAIL_SERVER_KEY=""
ENV INTERNAL_AUTH=""
ENV ALLOWED_DOMAINS="api.payment-service.com"
ENV FLASK_APP=inputs.py

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "inputs.py"]
