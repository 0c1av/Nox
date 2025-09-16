# Use slim Python base
FROM python:3.11-slim

# Install system dependencies
# - build-essential: compilers for C extensions
# - libffi-dev, libssl-dev: needed for cryptography
# - python3-dev: Python headers for compiling extensions
# - cargo: Rust compiler for packages like cryptography and tokenizers
# - default-mysql-client: for MySQL CLI tools
RUN apt-get update && apt-get install -y \
nmap \
iputils-ping \
default-mysql-client \
build-essential \
libffi-dev \
libssl-dev \
python3-dev \
cargo \
&& rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "flask_server.py"]
