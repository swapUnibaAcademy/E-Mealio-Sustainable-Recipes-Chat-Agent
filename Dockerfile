# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY projectRoot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# DEBUG: Show the actual file structure
RUN echo "=== Checking file structure ===" && \
    ls -la && \
    echo "=== Checking projectRoot ===" && \
    ls -la projectRoot/ && \
    echo "=== Checking if TelegramBot.py exists ===" && \
    test -f projectRoot/TelegramBot.py && echo "✅ TelegramBot.py found" || echo "❌ TelegramBot.py NOT found"

# Set default command
CMD ["python", "-u", "projectRoot/TelegramBot.py"]