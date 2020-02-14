import flask
import flask_wtf
import wtforms
import wshom

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField('Username', validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password', validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Sign In')

@wshom.app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flask.flash("Login requested for {user}".format(user=form.username.data))
        return flask.redirect(flask.url_for("index"))
    return flask.render_template("login.html", form=form)
