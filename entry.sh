#!/bin/bash
# Start ClamAV services
service clamav-daemon start
service clamav-freshclam start

# Then start the scanner.py Flask app with Gunicorn
exec gunicorn -w 4 -b 0.0.0.0:5000 scanner:app
