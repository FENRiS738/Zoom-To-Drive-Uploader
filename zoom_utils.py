import os

from zoomus import ZoomClient
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ACCOUNT_ID = os.getenv('ACCOUNT_ID')


def generate_token():
    client = ZoomClient(CLIENT_ID, CLIENT_SECRET, ACCOUNT_ID)
    token = client.__dict__['config']['token']
    return token

def get_downloadable_url(token, recording_id):
    download_url = f"https://zoom.us/recording/download/{recording_id}"
    download_url_with_token = f"{download_url}?access_token={token}"
    return download_url_with_token


    
if __name__ == "__main__":
    recording_id="1311d1d6-5a41-4aaf-9d96-e7eb48dca532"
    token = generate_token()
    print(token)
    # get_downloadable_url(token, recording_id)
