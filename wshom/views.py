import flask
from flask import Blueprint
import flask_login
import werkzeug.security
from wshom.model import User
from wshom.extensions import db, login_manager
import wshom.forms
from flask_login import current_user

blueprint = Blueprint("public", __name__, static_folder="../static")

login_manager.login_view = "public.login"

@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = wshom.forms.LoginForm()
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
    form = wshom.forms.RegisterForm()
    if form.validate_on_submit():
        password_hash = werkzeug.security.generate_password_hash(form.password.data)
        user = User(username=form.username.data,
                    password_hash=password_hash,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flask.flash("Registered!")
        flask_login.login_user(user, remember=True)
        return flask.redirect(flask.url_for("public.profile"))
    else:
        return flask.render_template("register.html", form=form)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@blueprint.route("/")
def index():
    return flask.render_template("index.html")

@blueprint.route("/friends", methods=["GET", "POST"])
@flask_login.login_required
def friends():
    add_friend_form = wshom.forms.AddFriendForm()
    delete_friend_form = wshom.forms.DeleteFriendForm()

    if add_friend_form.submit_add.data and add_friend_form.validate_on_submit():
        user = User.query.filter_by(username=add_friend_form.add_username.data).one()
        current_user.friends.append(user)
        db.session.commit()

    if delete_friend_form.submit_delete.data and delete_friend_form.validate_on_submit():
        user = User.query.filter_by(username=delete_friend_form.delete_username.data).one()
        current_user.friends.remove(user)
        db.session.commit()

    friends = current_user.friends
    delete_friend_forms = [wshom.forms.DeleteFriendForm(delete_username=f.username) for f in friends]
    return flask.render_template("friends.html", add_friend_form=add_friend_form, friends=zip(friends, delete_friend_forms), delete_friend_form=delete_friend_form)

@blueprint.route("/profile", methods=["GET", "POST"])
@flask_login.login_required
def profile():
    form = wshom.forms.ProfileForm(email=current_user.email, display_name=current_user.display_name, timezone=current_user.timezone, min_interval=current_user.min_interval, active=current_user.active)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.display_name = form.display_name.data
        current_user.timezone = form.timezone.data
        current_user.min_interval = form.min_interval.data
        current_user.active = form.active.data
        db.session.commit()
        flask.flash("Profile updated")
    return flask.render_template("profile.html", form=form)

