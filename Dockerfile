# Multi-stage lightweight Docker image for Building and Monitoring Honeypot
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=80 \
    HONEYPOT_LOG=/app/honeypot.log

# Set work directory
WORKDIR /app

# Install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose web service port
EXPOSE 80

# Run honeypot web decoy
CMD ["python", "app.py"]
