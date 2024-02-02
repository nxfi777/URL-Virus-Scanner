from flask import Flask, request, jsonify
import requests
import os
from subprocess import Popen, PIPE

app = Flask(__name__)

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
        os.remove(local_filename)  # Clean up the downloaded file
        parsed_results = parse_scan_results(scan_results)
        return jsonify(parsed_results)
    except Exception as e:
        return jsonify({"error": str(e)})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)