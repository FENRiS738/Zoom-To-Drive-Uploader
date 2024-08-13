import os
from threading import Thread

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from zoom_utils import generate_token, get_downloadable_url, background_upload

load_dotenv()

app = Flask(__name__)

RCLONE_CONFIG_PATH = os.getenv('RCLONE_CONFIG_PATH')
DESTINATION_PATH = os.getenv('DESTINATION_PATH')

@app.get('/')
def root():
    return jsonify({"message": "Server is running..."}), 200

@app.get('/upload')
def upload_file():
    try: 
        file_id = request.args['file_id']
        file_name = request.args['file_name']
        
        rclone_config = RCLONE_CONFIG_PATH
        file_name = f"{file_name}.mp4"
        destination = f'{DESTINATION_PATH}/{file_name}'
        
        token = generate_token()
        file_url = get_downloadable_url(token, file_id)

        background_task = Thread(target=background_upload,  args=(app, file_url, destination, rclone_config,))
        background_task.start()

        return jsonify({"message": "Upload process started!"}), 200
    except Exception as ex:
        return jsonify({
            "message" : "Something went wrong",
            "error" : ex
        }), 400


if __name__ == '__main__':
    app.run(debug=True)
