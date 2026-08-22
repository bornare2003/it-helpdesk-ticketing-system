import os

from flask import Flask
from flask_cors import CORS

from config import config_map
from models import db


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    # Make sure the instance folder (holds the SQLite file) exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from routes.api import api_bp
    from routes.views import views_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(e):
        from flask import request, jsonify, render_template
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))