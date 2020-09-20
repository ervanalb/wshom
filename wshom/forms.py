import flask_wtf
import wtforms
from wshom.model import User

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Sign In")

class RegisterForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.DataRequired()])
    password2 = wtforms.PasswordField("Re-type password", validators=[wtforms.validators.DataRequired(), wtforms.validators.EqualTo("password", message="Passwords do not match")])
    submit = wtforms.SubmitField("Register")

    def validate_username(self, field):
        if User.query.filter_by(username=self.username.data).first():
            raise wtforms.ValidationError("Username already taken")
