FROM python:3.12-slim

# Ignore pip warnings about running as root
ENV PIP_ROOT_USER_ACTION=ignore

# Install gpg for signing commits
RUN apt-get update && apt-get install -y --no-install-recommends \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# Install torch requirements
COPY torch.requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r torch.requirements.txt

# Install development requirements
COPY development.requirements.txt ./
RUN pip install --no-cache-dir -r development.requirements.txt

# Install main requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Initialize data directory
RUN mkdir ./data
RUN touch ./data/db.sqlite3
