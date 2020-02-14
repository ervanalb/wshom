import flask
import flask_wtf
import wtforms
import flask_login
import werkzeug.security
from wshom import app, db

login_manager = flask_login.LoginManager(app)

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('Username', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Sign In')

class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def check_password(password):
        return werkzeug.security.check_password_hash(self.password_hash, password)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.flash('Invalid username or password')
            return flask.redirect(flask.url_for("login"))
        else:
            flask_login.login_user(user, remember=True)
            return flask.redirect(flask.url_for("index"))
    return flask.render_template("login.html", form=form)

@app.route("/logout", methods=["POST"])
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("index"))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
