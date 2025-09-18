import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db

def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    max_mb = int(os.getenv("MAX_CONTENT_LENGTH_MB", "20"))
    app.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 5,
        "max_overflow": 10,
    }
    db.init_app(app)

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("instance", exist_ok=True)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.tracks import tracks_bp
    app.register_blueprint(tracks_bp)

    return app
