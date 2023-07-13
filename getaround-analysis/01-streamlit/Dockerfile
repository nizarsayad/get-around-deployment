# app/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim as base

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add all files to /app
COPY . /app

# Run the command to start the app
CMD streamlit run --server.port $PORT app.py
