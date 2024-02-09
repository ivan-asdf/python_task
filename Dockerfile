# Use an official Python runtime as a parent image
FROM python:3.11 AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt



FROM base AS prod
# Set the working directory in the container
WORKDIR /code
# Copy the current directory contents into the container at /app
COPY . /code
