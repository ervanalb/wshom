import flask
from flask import Blueprint
import flask_login
import werkzeug.security
from wshom.model import User
from wshom.extensions import db, login_manager
from wshom.forms import LoginForm, RegisterForm

blueprint = Blueprint("public", __name__, static_folder="../static")

@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash("Invalid username or password")
            return flask.redirect(flask.url_for("public.login"))
        else:
            flask_login.login_user(user, remember=True)
            return flask.redirect(flask.url_for("public.index"))
    return flask.render_template("login.html", form=form)

@blueprint.route("/logout", methods=["POST"])
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("public.index"))

@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = werkzeug.security.generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flask.flash("Registered!")
        flask_login.login_user(user, remember=True)
        return flask.redirect(flask.url_for("public.index"))
    else:
        return flask.render_template("register.html", form=form)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@blueprint.route("/")
def index():
    return flask.render_template("index.html")
