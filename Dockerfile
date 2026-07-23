# Production Dockerfile for Medigen backend
# -------------------------------------------------
FROM python:3.12-slim AS base

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    USER_ID=1001 \
    GROUP_ID=1001

# Install OS-level dependencies (curl for health checks, OpenCV libs)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for container security
RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -m -u ${USER_ID} -g appuser appuser

# Set work directory
WORKDIR /app

# Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script into work directory and make it executable
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Run migrations and start the server
ENTRYPOINT ["./entrypoint.sh"]
