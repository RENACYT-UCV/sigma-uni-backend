import firebase_admin
from firebase_admin import credentials, db

class FirebaseDB:
    def __init__(self, credential_path, database_url):
        # Verifica si ya existe una app Firebase inicializada
        if not firebase_admin._apps:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })

        # Referencia raíz de la base de datos
        self.ref = db.reference()

    def write_record(self, path, data):
     print(f"Escribiendo en: {path} → {data}")
     ref = db.reference(path)
     ref.set(data)


    def read_record(self, path):
     ref = db.reference(path)
     return ref.get()


    def update_record(self, path, data):
        # Actualiza datos en la ruta especificada
        self.ref.child(path).update(data)

    def delete_record(self, path):
        # Elimina datos en la ruta especificada
        self.ref.child(path).delete()
