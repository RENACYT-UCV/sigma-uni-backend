from functools import wraps
from flask import request, jsonify
from utils.jwt_manager import verify_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return jsonify({"status": "error", "message": "Token no encontrado"}), 401
        user_data = verify_token(token)
        if not user_data:
            return jsonify({"status": "error", "message": "Token inválido o expirado"}), 401
        return f(usuario=user_data, *args, **kwargs)
    return decorated_function
