#!/bin/bash
# Start ClamAV services
service clamav-daemon start
service clamav-freshclam start

# Then start the scanner.py Flask app
exec python scanner.py
