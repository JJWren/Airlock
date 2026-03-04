# Stage 1: Get the Syft binary
FROM anchore/syft:v1.0.1 as syft-binary

# Stage 2: Build the Airlock API
FROM python:3.14-slim
WORKDIR /app

# Install system dependencies for Subprocess and Networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the Syft binary from Stage 1 to the system PATH
COPY --from=syft-binary /usr/local/bin/syft /usr/local/bin/syft

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Start the FastAPI server
# Use the PORT environment variable passed from docker-compose
# We default to 8000 if nothing is provided
ENV PORT=8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
