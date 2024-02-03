from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth
import requests
import os
from subprocess import Popen, PIPE
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

TOKEN = os.environ.get('AUTH_TOKEN', 'default-token')

@auth.verify_token
def verify_token(token):
    if token == TOKEN:
        return True
    return None

def scan_file(file_path):
    process = Popen(['clamdscan', '--fdpass', file_path], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')

def parse_scan_results(results):
    """
    Parse clamdscan output to determine if file is infected and list detected viruses
    """
    lines = results.split('\n')
    file_scan_result = lines[0].split(': ')[1]
    viruses = []
    infected = False
    if file_scan_result != 'OK':
        infected = True
        # Extract the virus name from the clamdscan output
        viruses.append(file_scan_result.split(' FOUND')[0])
    return {'infected': infected, 'viruses': viruses}

@app.route('/scan', methods=['POST'])
@auth.login_required
def scan_url():
    try:
        file_url = request.json['url']
        local_filename = file_url.split('/')[-1]
        # Stream download to handle large files
        with requests.get(file_url, stream=True) as r:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        scan_results = scan_file(local_filename)
        print(scan_results)
        os.remove(local_filename)  # Clean up the downloaded file
        parsed_results = parse_scan_results(scan_results)
        return jsonify(parsed_results)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/scan_files', methods=['POST'])
@auth.login_required
def scan_files():
    try:
        files = request.files.getlist("files")
        results = []
        for file in files:
            # Save file to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp_file.name)
            # Scan the file
            scan_results = scan_file(temp_file.name)
             print(scan_results)
            # Clean up the temporary file
            os.unlink(temp_file.name)
            parsed_results = parse_scan_results(scan_results)
            results.append(parsed_results)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"})
