from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import Required, Email, Regexp, EqualTo,Length
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('keep me logged-in')
    submit = SubmitField('Log-In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, ''numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    about_me = TextAreaField('About Me', validators=[Required()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username= field.data).first():
            raise ValidationError("Username alraedy in use.")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[Required()])
    password=PasswordField('New password', validators=[Required(), EqualTo('password2',message='Password must match.')])

    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Reset-Password')
