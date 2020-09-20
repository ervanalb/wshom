import flask
import flask_sqlalchemy
import wshom.config
from wshom.extensions import db, login_manager
import wshom.config
import wshom.views

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

def register_blueprints(app):
    app.register_blueprint(wshom.views.blueprint)

def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(wshom.config.Config)
    register_extensions(app)
    register_blueprints(app)
    return app

def create_db(app):
    with app.app_context():
        db.create_all()
