# Production Dockerfile for Medigen backend
# -------------------------------------------------
# Use an official lightweight Python image.
FROM python:3.12-slim AS base

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install OS-level dependencies required by OpenCV and other packages
# Clean up apt lists to keep the image small.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy application code
COPY . .

# Expose the port that Render (or any platform) will assign
EXPOSE ${PORT:-8000}

# Run migrations and start the server
ENTRYPOINT ["/entrypoint.sh"]