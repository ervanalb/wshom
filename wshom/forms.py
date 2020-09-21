import flask_wtf
import wtforms
from wshom.model import User
from flask_login import current_user

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

class AddFriendForm(flask_wtf.FlaskForm):
    add_username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    submit_add = wtforms.SubmitField("Add Friend")

    def validate_add_username(self, field):
        user = User.query.filter_by(username=self.add_username.data).first()
        if user is None:
            raise wtforms.ValidationError("User not found")
        if user == current_user:
            raise wtforms.ValidationError("That's you")
        if user in current_user.friends:
            raise wtforms.ValidationError("User is already a friend")

class DeleteFriendForm(flask_wtf.FlaskForm):
    delete_username = wtforms.HiddenField("Username", validators=[wtforms.validators.DataRequired()])
    submit_delete = wtforms.SubmitField("[X]")

    def validate_delete_username(self, field):
        user = User.query.filter_by(username=self.delete_username.data).first()
        if user is None:
            raise wtforms.ValidationError("User not found")
        if user == current_user:
            raise wtforms.ValidationError("That's you")
        if user not in current_user.friends:
            raise wtforms.ValidationError("User is not a friend")
