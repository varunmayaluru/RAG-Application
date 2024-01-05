# Use an official Python runtime as a base image
FROM python:3.11.4-slim-buster

# Create the directory within the container image from the app code
RUN mkdir /usr/src/app

# Copy the requriements file into the container at /app
COPY ../requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /usr/src/app

# Set the working directory to /app
WORKDIR /usr/src/app

