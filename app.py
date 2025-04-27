import os
from dotenv import load_dotenv
from urllib.parse import quote
from mongoengine import connect

folders = [
    "storage",
    "storage/docs"
    "storage/images",
    "storage/models",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

load_dotenv()

APP_URL = os.environ.get('APP_URL')
APP_KEY = os.environ.get('APP_KEY')

MONGODB_HOST = os.environ.get('MONGODB_HOST')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')    
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
MONGODB_AUTHDB = os.environ.get('MONGODB_AUTHDB')
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE')

KIRIMKAN_URL = os.environ.get('KIRIMKAN_URL')
KIRIMKAN_API_KEY = os.environ.get('KIRIMKAN_API_KEY')

try:
    if not MONGODB_USERNAME or not MONGODB_PASSWORD or not MONGODB_AUTHDB:
        connection_string = f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}/'
    else:
        connection_string = f'mongodb://{MONGODB_USERNAME}:{quote(MONGODB_PASSWORD)}@{MONGODB_HOST}:{MONGODB_PORT}/?directConnection=true&authSource={MONGODB_AUTHDB}'
    
    connect(db=MONGODB_DATABASE, host=connection_string)
except Exception as e:
    exit(e)