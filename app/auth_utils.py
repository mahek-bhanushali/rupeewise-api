from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .extensions import db
from .models import User


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=current_app.config["TOKEN_EXPIRY_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(view):
    """Decorator: requires 'Authorization: Bearer <token>' and sets g.current_user."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = header.split(" ", 1)[1]
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = db.session.get(User, int(data["sub"]))
        if user is None:
            return jsonify({"error": "User not found"}), 401

        g.current_user = user
        return view(*args, **kwargs)

    return wrapper
