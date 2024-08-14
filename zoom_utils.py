import os
import subprocess
import requests

from flask import jsonify
from dotenv import load_dotenv
from celery_config import celery
from zoomus import ZoomClient

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def generate_token():
    client = ZoomClient(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    token = client.__dict__['config']['token']
    return token

def get_downloadable_url(token, recording_id):
    download_url = f"https://zoom.us/recording/download/{recording_id}"
    download_url_with_token = f"{download_url}?access_token={token}"
    return download_url_with_token

@celery.task
def background_upload(file_url, destination, rclone_config):
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
        call_webhook({
            'message': f'Successfully uploaded {file_url} to {destination}.'
        })
    else:
        call_webhook({
            'message': f'Failed to upload {file_url}: {result.stderr.decode()}'
        })

def call_webhook(payload):
    try:
        webhook_url = WEBHOOK_URL 
        result = requests.post(webhook_url, json=payload)
        result.raise_for_status()
        return jsonify({"message": "Successfully called webhook."}), 200
    except requests.exceptions.RequestException as ex:
        return jsonify({"message": "Failed to call webhook.", "error": str(ex)}), 400
