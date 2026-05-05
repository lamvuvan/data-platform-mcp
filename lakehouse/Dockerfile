FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for SASL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libsasl2-dev \
    libsasl2-modules \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment variables file
# COPY .env .
# Set environment variables
# ENV $(cat .env | xargs)

# Copy server files
COPY mcp_config.py .
COPY mcp_server.py .

EXPOSE 8000

# Set the command to run the server with the specified parameters
CMD ["python3.10", "mcp_server.py"]
