# Use the base image with PyTorch dependencies pre-installed
FROM ghcr.io/cs24-1/cs24-1-bot-base:latest

# Metadata
LABEL org.opencontainers.image.source=https://github.com/cs24-1/cs24-1-bot

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements/requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary application files
COPY src/ /app/src/

# Add data volume
VOLUME /app/data

# Set timezone
ENV TZ=Europe/Berlin

# Add src to Python path
ENV PYTHONPATH=/app/src

# Define environment variable
ENV DB_FILE_PATH='/app/data/db.sqlite3'

# Change to src directory for proper context
WORKDIR /app/src

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
