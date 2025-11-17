# Use Ubuntu 20.04 as base
FROM ubuntu:20.04

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt /app/

# Install required packages and Python dependencies
RUN apt-get update -y \
    && apt-get install -y python3-pip python3-dev default-libmysqlclient-dev build-essential mysql-client curl \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . /app

# Expose port 81 for Flask
EXPOSE 81

# Run the Flask application
CMD ["python3", "app.py"]
