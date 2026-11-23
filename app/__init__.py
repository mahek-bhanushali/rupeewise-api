from flask import Flask, jsonify

from config import Config
from .extensions import db


def create_app(config_class=Config):
    """Application factory: builds and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from .routes.auth import auth_bp
    from .routes.expenses import expenses_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(expenses_bp, url_prefix="/api/expenses")

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def health():
        return jsonify({"status": "ok", "service": "expense-tracker-api"})

    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
