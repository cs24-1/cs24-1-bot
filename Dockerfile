# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Metadata
LABEL org.opencontainers.image.source=https://github.com/TheItsNameless/cs24-1-bot

# Set the working directory in the container
WORKDIR /app

# Copy the torch requirements file into the container at /app
COPY torch.requirements.txt /app

# Install specific torch version
RUN pip install --no-cache-dir -r torch.requirements.txt

# Copy the requirements file into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Add data volume
VOLUME /app/data

# Set timezone
ENV TZ=Europe/Berlin

# Define environment variable
ENV DISCORD_TOKEN=''
ENV CUR_SERVER=''
ENV MENSA_CHANNEL=''
ENV MEME_CHANNEL=''
ENV DB_FILE_PATH='/app/data/db.sqlite3'

# Run bot.py when the container launches
CMD ["python", "-u", "main.py"]