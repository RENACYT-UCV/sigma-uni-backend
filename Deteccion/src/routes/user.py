from flask import Blueprint, jsonify

from config.firebase import db

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = db.read_record('/users')  # Fetch users from Firebase

    return jsonify({
        "message": "List of all users",
        "users": users
    })
