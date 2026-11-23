from flask import Blueprint, jsonify, request

from ..auth_utils import create_token
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if len(username) < 3 or len(username) > 50:
        return jsonify({"error": "username must be 3-50 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already taken"}), 409

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "id": user.id}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(username=str(data.get("username", "")).strip()).first()

    if user is None or not user.check_password(str(data.get("password", ""))):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"token": create_token(user.id)}), 200
