import flask_wtf
import wtforms
import wtforms.fields.html5
import wtforms.validators
from wshom.model import User
from flask_login import current_user
import pytz
import string

class LoginForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Sign In")

class RegisterForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Username", validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=3, max=10)])
    password = wtforms.PasswordField("Password", validators=[wtforms.validators.Length(min=6)])
    password2 = wtforms.PasswordField("Re-type password", validators=[wtforms.validators.DataRequired(), wtforms.validators.EqualTo("password", message="Passwords do not match")])
    email = wtforms.fields.html5.EmailField("Email", validators=[wtforms.validators.Email()])
    submit = wtforms.SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=self.email.data).first():
            raise wtforms.ValidationError("Email already in use")

    def validate_username(self, field):
        allowed_characters = string.ascii_lowercase + string.digits + "_"

        if any(c not in allowed_characters for c in self.username.data):
            raise wtforms.ValidationError("Username may only contain lowercase letters, digits, and undescores.")

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

class ProfileForm(flask_wtf.FlaskForm):
    tz_choices = [("", "unspecified")] + [(tzname, tzname.replace("_", " ")) for tzname in pytz.common_timezones]

    email = wtforms.StringField("Email", validators=[wtforms.validators.Email()])
    display_name = wtforms.StringField("Display Name", validators=[wtforms.validators.Length(max=240)])
    timezone = wtforms.SelectField("Timezone", choices=tz_choices, validators=[wtforms.validators.AnyOf(set(val for (val, _) in tz_choices), "Not a valid timezone")])
    min_interval = wtforms.fields.html5.IntegerField("Minimum interval between hangouts (days)", validators=[wtforms.validators.NumberRange(3, 12, "Value must be between %(min)s and %(max)s")])
    active = wtforms.BooleanField("Active")
    submit = wtforms.SubmitField("Update")

    def validate_email(self, field):
        if User.query.filter_by(email=self.email.data).first():
            raise wtforms.ValidationError("Email already in use")

