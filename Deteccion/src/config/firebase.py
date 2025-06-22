import os
import firebase_admin
from firebase_admin import credentials, db


class FirebaseDB:
    def __init__(self, cred_path, database_url):
        """
        Initialize FirebaseDB with the path to the Firebase credentials.
        
        :param cred_path: Path to the Firebase service account key JSON file.
        """
        self.cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(self.cred, {
            'databaseURL': database_url
        })

    def write_record(self, path, data):
        ref = db.reference(path)
        ref.set(data)

    def read_record(self, path):
        ref = db.reference(path)
        return ref.get()

    def update_record(self, path, data):
        ref = db.reference(path)
        ref.update(data)

    def delete_record(self, path):
        ref = db.reference(path)
        ref.delete()


path = os.getenv('FIREBASE_CREDENTIALS_PATH')
url = os.getenv('FIREBASE_DATABASE_URL')

db = FirebaseDB(path, url)
