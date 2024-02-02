FROM python:3.9-slim

# Install ClamAV
RUN apt-get update &&\
    apt-get install -y clamav clamav-daemon &&\
    freshclam

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Flask and requests using pip
RUN pip install Flask requests

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "scanner.py"]