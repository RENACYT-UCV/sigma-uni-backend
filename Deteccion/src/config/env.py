import os
from dotenv import load_dotenv


load_dotenv()


class FirebaseConfig:
    CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')

env_config = {
    'FIREBASE': FirebaseConfig
}
