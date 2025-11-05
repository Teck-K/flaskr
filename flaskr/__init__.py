
from flask import Flask
from . import auth, db, blog

def create_app(database: str = db.SQLITE_DB_FILE) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = database

    app.secret_key = "dev"
    app.jinja_options["autoescape"] = True

    @app.route("/ping")
    def ping():
        return "pong"

    app.teardown_appcontext(db.close_db)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    return app
