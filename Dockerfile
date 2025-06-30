FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY crawler/requirements.txt .
COPY dashboard/requirements.txt ./dashboard_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r dashboard_requirements.txt
RUN pip install --no-cache-dir flask

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Create shared directory
RUN mkdir -p shared

# Set environment variables
ENV DISPLAY=:99
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Make start script executable
RUN chmod +x crawler/start.sh

# Expose port
EXPOSE 8080

# Default command - run the web service
CMD ["python", "crawler_service.py"] 