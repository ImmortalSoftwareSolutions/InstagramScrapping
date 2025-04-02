# Use an official Python 3.11 slim image as the base
FROM python:3.11-slim

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (no --with-deps needed, as deps are above)
RUN python -m playwright install

# Copy the rest of your application
COPY . .

# Define the start command (replace with your actual command)
CMD ["python", "main.py"]