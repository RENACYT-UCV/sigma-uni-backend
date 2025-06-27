# Importaciones necesarias
import os
import random # Para generar códigos aleatorios
import string # Para caracteres de código
from flask import Flask, jsonify, render_template, request, make_response, url_for, redirect, send_from_directory
from dotenv import load_dotenv
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import jwt
import pymysql
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "sigma_db"),
        cursorclass=pymysql.cursors.DictCursor
    )


# Cargar las variables de entorno del archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)

# --- Configuración de Flask ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# --- Configuración de MySQL ---
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # Para obtener resultados como diccionarios

# Inicializar la extensión MySQL
mysql = MySQL(app)

# Inicializar Bcrypt para el hasheo de contraseñas
bcrypt = Bcrypt(app)

# --- Configuración de Flask-Mail ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Inicializar la extensión Mail
mail = Mail(app)

# --- Decorador para rutas protegidas con JWT en cookies ---
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token') # Obtener el token de la cookie

        if not token:
            return jsonify({"message": "Token de autenticación faltante o inválido."}, 401)

        try:
            # Decodificar el token usando la SECRET_KEY de la aplicación
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Almacenar la información del usuario decodificada en el objeto request
            request.user = data
        except jwt.ExpiredSignatureError:
            # Si el token expira, redirigir al login (en el frontend) o devolver un error
            response = make_response(jsonify({"message": "Sesión expirada. Por favor, inicie sesión de nuevo."}), 401)
            response.set_cookie('token', '', expires=0, httponly=True, secure=False, samesite='Lax')
            return response
        except jwt.InvalidTokenError:
            response = make_response(jsonify({"message": "Token inválido. Por favor, inicie sesión de nuevo."}), 401)
            response.set_cookie('token', '', expires=0, httponly=True, secure=False, samesite='Lax')
            return response
        
        return f(*args, **kwargs)
    return decorated

# --- Función auxiliar para obtener ID de lección por nombre ---
def get_lesson_id_by_name(lesson_name):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM lecciones WHERE nombre = %s", (lesson_name,))
        lesson = cur.fetchone()
        cur.close()
        if lesson:
            return lesson['id']
        return None
    except Exception as e:
        print(f"Error al obtener ID de lección por nombre: {e}")
        return None

# --- Función auxiliar para verificar si una lección está completada por el usuario ---
def is_lesson_completed(user_id, lesson_name):
    lesson_id = get_lesson_id_by_name(lesson_name)
    if not lesson_id:
        return False
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT completado FROM lecciones_usuario WHERE usuario_id = %s AND leccion_id = %s",
            (user_id, lesson_id)
        )
        result = cur.fetchone()
        cur.close()
        # Devuelve True si se encuentra el registro y 'completado' es True
        return bool(result and result['completado'])
    except Exception as e:
        print(f"Error al verificar estado de lección: {e}")
        return False


# --- Rutas (endpoints) para servir HTML ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('Registro.html')

@app.route('/login')
def login_page():
    return render_template('Login.html')

@app.route('/menu')
@jwt_required 
def menu_page():
    return render_template('Menu.html')

@app.route('/lessons/numbers')
@jwt_required
def numbers_lesson_page():
    user_id = request.user['user_id']
    lesson_already_completed = is_lesson_completed(user_id, 'números')
    return render_template('numerico.html', lesson_already_completed=lesson_already_completed)

@app.route('/lessons/letters')
@jwt_required
def letters_lesson_page():
    user_id = request.user['user_id']
    lesson_already_completed = is_lesson_completed(user_id, 'letras')
    return render_template('abecedario.html', lesson_already_completed=lesson_already_completed)

@app.route('/lessons/food')
@jwt_required
def food_lesson_page():
    user_id = request.user['user_id']
    lesson_already_completed = is_lesson_completed(user_id, 'comidas')
    return render_template('Alimentos.html', lesson_already_completed=lesson_already_completed)

@app.route('/lessons/phrases')
@jwt_required
def phrases_lesson_page():
    user_id = request.user['user_id']
    lesson_already_completed = is_lesson_completed(user_id, 'preguntas')
    return render_template('frases.html', lesson_already_completed=lesson_already_completed)

@app.route('/coments')
@jwt_required
def coments_page():
    return render_template('Comentarios.html')

@app.route('/forgot_password')
def forgot_password_page():
    return render_template('Correo.html')

@app.route('/verify_code')
def verify_code_page():
    return render_template('Codigo.html')

@app.route('/change_password_form') # Ruta para el formulario de cambio de contraseña después de la verificación
def change_password_form_page():
    # El frontend debe pasar un token temporal para acceder a esta página si es necesario,
    # o gestionarlo completamente con sessionStorage para más seguridad y SPA-like behavior.
    return render_template('CambioContra.html')



@app.route('/admin/dashboard')
def serve_admin_dashboard():
    path = os.path.join(app.root_path, 'ProyectoFrontBack', 'Administrador')
    return send_from_directory(path, 'dashboardAdmin.html')

@app.route('/admin/static/<path:filename>')
def admin_static_files(filename):
    return send_from_directory(
        os.path.join(app.root_path, 'ProyectoFrontBack', 'Administrador'),
        filename
    )


@app.route('/admin/manage_users')
@jwt_required
def admin_manage_users_page():
    return render_template('gestionUsuarios.html')

@app.route('/admin/manage_admins')
@jwt_required
def admin_manage_admins_page():
    return render_template('gestionAdministradores.html')


# --- Rutas (endpoints) de API ---

@app.route('/api')
def api_home():
    return jsonify({"message": "Bienvenido al backend de SIGMA-UNI!"})

@app.route('/api/test_db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
        cur.close()
        return jsonify({"message": "Conexión a MySQL exitosa!", "version": version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    nombres = data.get('nombres')
    apellidos = data.get('apellidos')
    correo = data.get('correo')
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    dni = data.get('dni')
    fecha_nacimiento = data.get('fecha_nacimiento')
    telefono = data.get('telefono')
    direccion = data.get('direccion')
    
    if not (nombres and apellidos and correo and usuario and contrasena):
        return jsonify({"error": "Todos los campos obligatorios (Nombres, Apellidos, Correo, Usuario, Contraseña) son requeridos."}), 400

    try:
        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')
        
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT id FROM usuarios WHERE correo = %s OR usuario = %s", (correo, usuario))
        existing_user = cur.fetchone()
        if existing_user:
            cur.close()
            return jsonify({"error": "El correo electrónico o el nombre de usuario ya están registrados."}), 409

        sql = """INSERT INTO usuarios (nombres, apellidos, correo, usuario, contrasena, dni, fecha_nacimiento, telefono, direccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (nombres, apellidos, correo, usuario, hashed_password, dni, fecha_nacimiento, telefono, direccion))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"message": "Usuario registrado exitosamente!"}), 201
        
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return jsonify({"error": "Error interno del servidor al registrar el usuario."}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()

    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not (username_or_email and password):
        return jsonify({"error": "Usuario/Correo y Contraseña son requeridos."}), 400

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT id, usuario, correo, contrasena, rol, estado 
            FROM usuarios 
            WHERE usuario = %s OR correo = %s
        """, (username_or_email, username_or_email))
        user = cur.fetchone()
        cur.close()

        if user:
            if bcrypt.check_password_hash(user['contrasena'], password):
                payload = {
                    'user_id': user['id'],
                    'username': user['usuario'],
                    'email': user['correo'],
                    'role': user['rol'],
                    'exp': datetime.utcnow() + timedelta(hours=24),
                    'iat': datetime.utcnow()
                }

                # Codificar el token y asegurarse de que es un string
                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')

                # Crear la respuesta con la cookie JWT
                response = make_response(jsonify({
                    "message": "Inicio de sesión exitoso!",
                    "user_id": user['id'],
                    "username": user['usuario'],
                    "role": user['rol']
                }), 200)

                response.set_cookie(
                    'token',
                    token,
                    httponly=True,
                    secure=False,  # ✅ en producción: True con HTTPS
                    max_age=86400,  # 24 horas
                    samesite='Lax'
                )

                return response
            else:
                return jsonify({"error": "Credenciales inválidas."}), 401
        else:
            return jsonify({"error": "Credenciales inválidas."}), 401

    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        return jsonify({"error": "Error interno del servidor al iniciar sesión."}), 500



@app.route('/api/lessons/complete', methods=['POST'])
@jwt_required 
def complete_lesson():
    data = request.get_json()
    lesson_name = data.get('lesson_name')
    user_id = request.user['user_id']

    if not lesson_name:
        return jsonify({"error": "Nombre de la lección es requerido."}), 400

    lesson_id = get_lesson_id_by_name(lesson_name)
    if not lesson_id:
        return jsonify({"error": "Lección no encontrada en la base de datos."}), 404

    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO lecciones_usuario (usuario_id, leccion_id, completado) VALUES (%s, %s, TRUE)"
        cur.execute(sql, (user_id, lesson_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": f"Lección '{lesson_name}' marcada como completada."}), 200
    except Exception as e:
        if "Duplicate entry" in str(e) and "for key 'lecciones_usuario.UNIQUE'" in str(e):
            print(f"La lección '{lesson_name}' ya estaba completada por el usuario {user_id}. No se añade duplicado.")
            return jsonify({"message": f"La lección '{lesson_name}' ya ha sido marcada como completada para este usuario."}), 200
        print(f"Error al completar lección: {e}")
        return jsonify({"error": "Error interno del servidor al marcar la lección como completada."}), 500

@app.route('/api/comments', methods=['POST'])
@jwt_required 
def add_comment():
    data = request.get_json()
    comment_text = data.get('comentario')
    user_id = request.user['user_id']

    if not comment_text:
        return jsonify({"error": "El comentario no puede estar vacío."}), 400

    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO comentarios (usuario_id, comentario) VALUES (%s, %s)"
        cur.execute(sql, (user_id, comment_text))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Comentario enviado exitosamente."}), 201
    except Exception as e:
        print(f"Error al añadir comentario: {e}")
        return jsonify({"error": "Error interno del servidor al añadir el comentario."}), 500

@app.route('/api/comments', methods=['GET'])
@jwt_required 
def get_comments():
    try:
        cur = mysql.connection.cursor()
        sql = """
            SELECT c.comentario, c.fecha, u.nombres, u.apellidos, u.usuario
            FROM comentarios c
            JOIN usuarios u ON c.usuario_id = u.id
            ORDER BY c.fecha DESC
        """
        cur.execute(sql)
        comments = cur.fetchall()
        cur.close()
        
        if not comments:
            return jsonify([]), 204 # Devolver 204 No Content si no hay comentarios

        formatted_comments = []
        for comment in comments:
            fecha_dt = comment['fecha']
            formatted_date = fecha_dt.strftime('%Y-%m-%d %H:%M')
            
            nombre_completo = f"{comment['nombres']} {comment['apellidos']}" if comment['nombres'] and comment['apellidos'] else comment['usuario']
            
            formatted_comments.append({
                'comentario': comment['comentario'],
                'fecha': formatted_date,
                'autor_nombre': nombre_completo,
                'autor_usuario': comment['usuario']
            })
            
        return jsonify(formatted_comments), 200
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return jsonify({"error": "Error interno del servidor al obtener comentarios."}), 500

# --- API para la solicitud de recuperación de contraseña (Enviar Email con Código) ---
@app.route('/api/forgot_password_request', methods=['POST'])
def forgot_password_request():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "El correo electrónico es requerido."}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, usuario FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if not user:
            return jsonify({"error": "No existe un usuario con este correo electrónico."}), 404

        user_id = user['id']
        username = user['usuario']
        
        # Generar un código de verificación aleatorio (6 dígitos)
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Calcular tiempo de expiración (ej. 15 minutos)
        expires_at = datetime.utcnow() + timedelta(minutes=15)

        # Guardar el token en la tabla password_reset_tokens
        cur = mysql.connection.cursor()
        # Primero, limpiar cualquier token antiguo para este usuario
        cur.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user_id,))
        sql = "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)"
        cur.execute(sql, (user_id, verification_code, expires_at))
        mysql.connection.commit()
        cur.close()

        # Enviar el correo electrónico
        msg = Message("Recuperación de Contraseña - Código de Verificación",
                    recipients=[email])
        msg.body = (f"Hola {username},\n\n"
                    f"Tu código de verificación para cambiar tu contraseña es: {verification_code}\n\n"
                    "Este código expirará en 15 minutos.\n"
                    "Si no solicitaste este cambio, por favor ignora este correo.\n\n"
                    "Saludos,\nEquipo Sigma")
        
        mail.send(msg)
        
        return jsonify({"message": "Código de verificación enviado a su correo electrónico."}), 200

    except Exception as e:
        print(f"Error al solicitar recuperación de contraseña: {e}")
        return jsonify({"error": "Error interno del servidor al procesar la solicitud."}), 500

# --- API para verificar el código de recuperación ---
@app.route('/api/verify_reset_code', methods=['POST'])
def verify_reset_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')

    if not (email and code):
        return jsonify({"error": "Correo electrónico y código son requeridos."}), 400
    
    try:
        cur = mysql.connection.cursor()
        # Buscar el usuario por correo
        cur.execute("SELECT id FROM usuarios WHERE correo = %s", (email,))
        user = cur.fetchone()
        if not user:
            cur.close()
            return jsonify({"error": "Correo electrónico no encontrado."}), 404
        
        user_id = user['id']

        # Buscar el token de restablecimiento para el usuario y código
        cur.execute(
            "SELECT id, expires_at FROM password_reset_tokens WHERE user_id = %s AND token = %s",
            (user_id, code)
        )
        reset_token_entry = cur.fetchone()

        if not reset_token_entry:
            cur.close()
            return jsonify({"error": "Código de verificación inválido."}), 401

        # Verificar si el token ha expirado
        if datetime.utcnow() > reset_token_entry['expires_at']:
            cur.execute("DELETE FROM password_reset_tokens WHERE id = %s", (reset_token_entry['id'],))
            mysql.connection.commit()
            cur.close()
            return jsonify({"error": "Código de verificación ha expirado. Por favor, solicite uno nuevo."}), 401
        
        # Si el código es válido y no ha expirado, devolver el ID del token
        # Este ID será usado en la siguiente etapa para cambiar la contraseña
        cur.close()
        return jsonify({"message": "Código verificado exitosamente.", "reset_token_id": reset_token_entry['id']}), 200

    except Exception as e:
        print(f"Error al verificar código: {e}")
        return jsonify({"error": "Error interno del servidor al verificar el código."}), 500

# --- API para cambiar la contraseña ---
@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    reset_token_id = data.get('reset_token_id')
    new_password = data.get('new_password')

    if not (reset_token_id and new_password):
        return jsonify({"error": "ID de token de restablecimiento y nueva contraseña son requeridos."}), 400

    try:
        cur = mysql.connection.cursor()
        # Validar el reset_token_id y obtener el user_id asociado
        cur.execute(
            "SELECT user_id, expires_at FROM password_reset_tokens WHERE id = %s",
            (reset_token_id,)
        )
        token_info = cur.fetchone()

        if not token_info:
            cur.close()
            return jsonify({"error": "Token de restablecimiento inválido o ya utilizado."}), 401

        # Verificar si el token ha expirado (doble verificación por seguridad)
        if datetime.utcnow() > token_info['expires_at']:
            cur.execute("DELETE FROM password_reset_tokens WHERE id = %s", (reset_token_id,))
            mysql.connection.commit()
            cur.close()
            return jsonify({"error": "Token de restablecimiento ha expirado. Por favor, solicite uno nuevo."}), 401

        user_id = token_info['user_id']
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # Actualizar la contraseña del usuario
        cur.execute("UPDATE usuarios SET contrasena = %s WHERE id = %s", (hashed_password, user_id))
        mysql.connection.commit()

        # Invalidar/eliminar el token después de usarlo
        cur.execute("DELETE FROM password_reset_tokens WHERE id = %s", (reset_token_id,))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Contraseña actualizada exitosamente."}), 200

    except Exception as e:
        print(f"Error al restablecer contraseña: {e}")
        return jsonify({"error": "Error interno del servidor al restablecer la contraseña."}), 500


@app.route('/api/dashboard/puntajes')
def dashboard_puntajes():
    modo = request.args.get("modo", "semana")

    formatos = {
        "semana": "%Y-%m-%d",
        "mes": "%Y-%m",
        "año": "%Y"
    }

    formato = formatos.get(modo, "%Y-%m-%d")  # Default diario

    try:
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT DATE_FORMAT(fecha_completado, %s) AS fecha, COUNT(*) AS cantidad
                FROM lecciones_usuario
                WHERE completado = TRUE
                GROUP BY fecha
                ORDER BY fecha
            """, (formato,))
            resultados = cursor.fetchall()
        connection.close()
        return jsonify([{"fecha": r["fecha"], "cantidad": r["cantidad"]} for r in resultados])
    except Exception as e:
        print("Error en /api/dashboard/puntajes:", e)
        return jsonify({"error": "No se pudo cargar los puntajes"}), 500


    # Obtener el formato correspondiente, si no existe usa el diario
    formato = formatos.get(modo, "%Y-%m-%d")

    # Conexión a la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Consulta con parámetro de formato
    cursor.execute("""
        SELECT DATE_FORMAT(fecha_completado, %s) AS fecha, COUNT(*) AS cantidad
        FROM lecciones_usuario
        WHERE completado = TRUE
        GROUP BY fecha
        ORDER BY fecha
    """, (formato,))

    resultados = cursor.fetchall()

    # Convertir a JSON con claves
    datos = [{"fecha": fila["fecha"], "cantidad": fila["cantidad"]} for fila in resultados]

    connection.close()
    return jsonify(datos)

@app.route('/api/dashboard/usuarios')
def usuarios_dashboard():
    modo = request.args.get('modo', 'diario')

    if modo == 'diario':
        agrupador = "%Y-%m-%d"
    elif modo == 'semanal':
        agrupador = "%Y-%u"  # Año y número de semana
    elif modo == 'mensual':
        agrupador = "%Y-%m"
    else:
        return jsonify({"error": "Modo inválido"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT DATE_FORMAT(fecha_registro, %s) AS fecha, COUNT(*) AS cantidad
                FROM usuarios
                GROUP BY fecha
                ORDER BY fecha ASC
            """, (agrupador,))
            resultados = cursor.fetchall()

        # Verificamos si los resultados tienen formato correcto
        datos = [{"fecha": fila["fecha"], "cantidad": fila["cantidad"]} for fila in resultados]
        return jsonify(datos)
    
    except Exception as e:
        print(f"Error en /api/dashboard/usuarios: {e}")
        return jsonify({"error": "Error interno"}), 500
 

# --- Ruta para cerrar sesión (eliminar la cookie) ---
@app.route('/api/logout', methods=['POST'])
def logout_user():
    response = make_response(jsonify({"message": "Sesión cerrada exitosamente."}), 200)
    response.set_cookie('token', '', expires=0, httponly=True, secure=False, samesite='Lax')
    return response

@app.route('/api/usuarios')
def obtener_usuarios():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT CONCAT(nombres, ' ', apellidos) AS nombre, correo AS email, rol 
                FROM usuarios
            """)
            usuarios = cursor.fetchall()
        connection.close()
        return jsonify(usuarios)
    except Exception as e:
        print("Error al obtener usuarios:", e)
        return jsonify({"error": "No se pudo obtener usuarios"}), 500


# Esta parte asegura que la aplicación se ejecute solo si este script es el principal
# if __name__ == '__main__':
#     app.run(debug=True)

