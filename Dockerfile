FROM python:3.12-slim

# Install ClamAV
RUN apt-get update &&\
    apt-get install -y clamav clamav-daemon &&\
    freshclam

# Set the working directory in the container
WORKDIR /usr/src/app

# Install Flask and requests using pip
RUN pip install Flask requests Flask-HTTPAuth gunicorn

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

RUN chmod +x /usr/src/app/entry.sh

# Make the script the container's entrypoint
ENTRYPOINT ["/usr/src/app/entry.sh"]
