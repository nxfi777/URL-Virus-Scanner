#!/bin/bash
# Start ClamAV services
service clamav-daemon start
service clamav-freshclam start

# Then start the scanner.py Flask app with Gunicorn
exec gunicorn -b [::]:5000 scanner:app
