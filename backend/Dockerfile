# --- Stage 1: Builder ---
# This stage builds the Python virtual environment
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies
# --no-cache-dir ensures we don't store unnecessary cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install
# We copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Application ---
# This stage builds the final lightweight image
FROM python:3.10-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to include the venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 5000

# Set the command to run the application using Gunicorn
# Gunicorn is a production-ready WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]