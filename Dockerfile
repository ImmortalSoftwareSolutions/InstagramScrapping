# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    # Core dependencies for all browsers
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
    # Additional dependencies mentioned in error or commonly needed
    libxfixes3 \
    libx11-xcb1 \
    libxcursor1 \
    libxi6 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libfontconfig1 \
    # For WebKit and Firefox
    libwoff1 \
    libharfbuzz-icu0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Copy the rest of your application
COPY . .

# Define the start command (replace with your actual command)
CMD ["python", "main.py"]