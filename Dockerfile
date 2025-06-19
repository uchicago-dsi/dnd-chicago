# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for geopandas and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY uv.lock .

# Install uv and create virtual environment
RUN pip install uv && \
    python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -e . && \
    pip install jupyter notebook

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

# Default command
CMD ["bash"] 