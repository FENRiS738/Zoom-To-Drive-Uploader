import os
import subprocess

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from zoom_utils import generate_token, get_downloadable_url

load_dotenv()

app = Flask(__name__)

RCLONE_CONFIG_PATH = os.getenv('RCLONE_CONFIG_PATH')
DESTINATION_PATH = os.getenv('DESTINATION_PATH')

@app.get('/')
def root():
    return jsonify({"message": "Server is running..."}), 200

@app.get('/upload')
def upload_file():
    file_id = request.args['file_id']
    file_name = request.args['file_name']
    
    rclone_config = RCLONE_CONFIG_PATH
    file_name = f"{file_name}.mp4"
    destination = f'{DESTINATION_PATH}/{file_name}'
    
    token = generate_token()
    file_url = get_downloadable_url(token, file_id)

    command = [
        'rclone',
        'copyurl',
        file_url,
        destination,
        '--config',
        rclone_config
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        return jsonify({'message':f'Successfully uploaded {file_url} to {destination}.'}), 200
    else:
        return jsonify({'message':f'Failed to upload {file_url}: {result.stderr.decode()}'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
