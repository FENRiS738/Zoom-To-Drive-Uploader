import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from logging.handlers import RotatingFileHandler
from  threading import Thread
from zoom_utils import generate_token, get_downloadable_url, background_upload

load_dotenv()

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

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

        backgroud_task = Thread(target=background_upload, args=(app, file_url, destination, rclone_config,))
        backgroud_task.start()

        return jsonify({"message": "Upload process started!"}), 200
    except Exception as ex:
        app.logger.error(f"Upload failed: {str(ex)}")
        return jsonify({"message": "Something went wrong", "error": str(ex)}), 400

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    response.data = jsonify({
        "message": e.description,
        "error": str(e)
    }).data
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "message": "Internal Server Error",
        "error": str(e)
    }), 500

if __name__ == '__main__':
    if not app.debug:
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
    app.logger.info('Application startup')
    app.run(host='0.0.0.0', port=5000)
