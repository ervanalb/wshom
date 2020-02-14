import flask
import flask_wtf
import wtforms
import flask_login
import werkzeug.security
from wshom import app, db

login_manager = flask_login.LoginManager(app)

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Sign In")

class RegisterForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.DataRequired()])
    password2 = wtforms.PasswordField("Re-type password", validators=[wtforms.validators.DataRequired(), wtforms.validators.EqualTo("password", message="Passwords do not match")])
    submit = wtforms.SubmitField("Register")

    def validate_username(form, field):
        if User.query.filter_by(username=form.username.data).first():
            raise wtforms.ValidationError("Username already taken")

class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.password_hash, password)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash("Invalid username or password")
            return flask.redirect(flask.url_for("login"))
        else:
            flask_login.login_user(user, remember=True)
            return flask.redirect(flask.url_for("index"))
    return flask.render_template("login.html", form=form)

@app.route("/logout", methods=["POST"])
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("index"))

@app.route("/register", methods=["GET", "POST"])
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
        return flask.redirect(flask.url_for("index"))
    else:
        return flask.render_template("register.html", form=form)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
