# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv()

def get_credentials_path():
    raw_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if '\\' in raw_path:
        return raw_path.encode('unicode-escape').decode()
    return raw_path

if not firebase_admin._apps:
    cred_path = get_credentials_path()
    cred = credentials.Certificate(cred_path)
    firebase_app = firebase_admin.initialize_app(cred)
    
db = firestore.client()