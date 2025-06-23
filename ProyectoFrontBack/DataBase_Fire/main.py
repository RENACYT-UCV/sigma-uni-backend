from flask import Flask, request, jsonify
from Class_Firebase_DB import FirebaseDB
from flask_cors import CORS
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from firebase_admin import credentials, db


# 1. Inicializar Firebase
cred = credentials.Certificate("sigma-uni-ucv-firebase-adminsdk-fbsvc-6e3ea96815.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sigma-uni-ucv-default-rtdb.firebaseio.com/'
})

path = "sigma-uni-ucv-firebase-adminsdk-fbsvc-6e3ea96815.json"
url = "https://sigma-uni-ucv-default-rtdb.firebaseio.com/"
fb_db = FirebaseDB(path, url)

# 2. Crear la app de Flask
app = Flask(__name__)
CORS(app)


@app.route('/registro', methods=['POST'])
def registro():
    data = request.json
    nombre = data.get("nombre")
    correo = data.get("correo")
    usuario = data.get("usuario")
    contrasena = data.get("contrasena")

    if not all([nombre, correo, usuario, contrasena]):
        return jsonify({"status": "error", "message": "Campos incompletos"}), 400

    # ⚠️ VALIDAR si el correo o usuario ya existen
    usuarios = fb_db.read_record("usuarios")
    if usuarios:
        for u in usuarios.values():
            if u["correo"] == correo:
                return jsonify({"status": "error", "message": "Este correo ya está registrado"}), 409
            if u["usuario"] == usuario:
                return jsonify({"status": "error", "message": "Este usuario ya está registrado"}), 409

    # ✅ Si pasa validación, guardar
    fb_db.write_record(f"usuarios/{usuario}", {
        "nombre": nombre,
        "correo": correo,
        "usuario": usuario,
        "contrasena": contrasena
    })

    return jsonify({"status": "success", "message": "Usuario registrado correctamente"})



# 4. Ruta de login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_or_email = data.get("usuario")
    contrasena = data.get("contrasena")

    if not user_or_email or not contrasena:
        return jsonify({"status": "error", "message": "Credenciales incompletas"}), 400

    usuarios = fb_db.read_record("usuarios")
    if not usuarios:
        return jsonify({"status": "error", "message": "No hay usuarios registrados"}), 404

    for usuario, info in usuarios.items():
        if (info["usuario"] == user_or_email or info["correo"] == user_or_email) and info["contrasena"] == contrasena:
            return jsonify({"status": "success", "message": "Login exitoso", "nombre": info["nombre"]})

    return jsonify({"status": "error", "message": "Usuario o contraseña incorrecta"}), 401




@app.route('/verificar-codigo', methods=['POST'])
def verificar_codigo():
    data = request.json
    email = data.get('email')
    codigo_ingresado = data.get('codigo')

    if not email or not codigo_ingresado:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    # Lee el código guardado desde Firebase
    email_sanitizado = email.replace('.', '_')
    datos_codigo = fb_db.read_record(f"codigos_verificacion/{email_sanitizado}")

    if not datos_codigo:
        return jsonify({"status": "error", "message": "No se encontró un código para este correo"}), 404

    codigo_real = datos_codigo.get("codigo")
    usuario = datos_codigo.get("usuario")

    if codigo_ingresado == codigo_real:
        # ✅ El código coincide
        return jsonify({
            "status": "success",
            "message": "Código verificado correctamente",
            "usuario": usuario
        })
    else:
        return jsonify({"status": "error", "message": "Código incorrecto"}), 401


@app.route("/cambiar-contrasena", methods=["POST"])
def cambiar_contrasena():
    data = request.json
    usuario = data.get("usuario")
    nueva_contrasena = data.get("nuevaContrasena")

    if not usuario or not nueva_contrasena:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400
 

    # Actualizar en Firebase
    fb_db.update_record(f"usuarios/{usuario}", {
        "contrasena": nueva_contrasena
    })

    return jsonify({"status": "success", "message": "Contraseña actualizada correctamente"})

@app.route('/enviar-codigo', methods=['POST'])
def enviar_codigo():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Correo no proporcionado"}), 400

    # Verificar si el correo existe en la base de datos
    usuarios = fb_db.read_record("usuarios")
    if not usuarios:
        return jsonify({"status": "error", "message": "No hay usuarios registrados"}), 404

    usuario_encontrado = None
    for usuario, info in usuarios.items():
        if info["correo"].lower() == email.lower():
            usuario_encontrado = usuario
            break

    if not usuario_encontrado:
        return jsonify({"status": "error", "message": "Correo no registrado"}), 404

    # Generar código aleatorio de 4 dígitos
    codigo = str(random.randint(1000, 9999))

    # Guardar el código en Firebase temporalmente
    fb_db.write_record(f"codigos_verificacion/{email.replace('.', '_')}", {
        "codigo": codigo,
        "usuario": usuario_encontrado
    })

    # Enviar el código por correo
    try:
        remitente = "peraltasantistebanjose.2004@gmail.com"  # Cambia esto
        password = "mbqb rdtx emgs svxx"  # Usa una clave de app de Gmail

        mensaje = MIMEMultipart()
        mensaje['From'] = remitente
        mensaje['To'] = email
        mensaje['Subject'] = "Código de Verificación - Sigma"

        cuerpo = f"Hola,\n\nTu código de verificación para Sigma es: {codigo}\n\nGracias por usar nuestra plataforma."
        cuerpo_texto = MIMEText(cuerpo, "plain", "utf-8")
        mensaje.attach(cuerpo_texto)

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(mensaje)
        servidor.quit()

        return jsonify({"status": "success", "message": "Código enviado correctamente al correo"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al enviar el correo: {str(e)}"}), 500
    

@app.route('/prueba', methods=['GET'])
def prueba():
     fb_db.write_record("usuarios/testuser", {
        "nombre": "Test",
        "correo": "test@gmail.com",
        "usuario": "testuser",
        "contrasena": "1234"
    })
     return "Usuario de prueba guardado"


# 5. Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
