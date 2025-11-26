# Use the base image with PyTorch dependencies pre-installed
FROM ghcr.io/cs24-1/cs24-1-bot-base:latest

# Set timezone
ENV TZ=Europe/Berlin

# Ignore pip warnings about running as root
ENV PIP_ROOT_USER_ACTION=ignore

# Install gpg for signing commits
RUN apt-get update && apt-get install -y --no-install-recommends \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# Install development requirements
COPY requirements/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install main requirements
COPY requirements/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
