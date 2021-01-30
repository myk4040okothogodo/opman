from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField,SelectField
from wtforms.validators import Required, Email, Regexp, EqualTo, Length
from wtforms import ValidationError
from ..models import Account, Opportunity,User,Role


class AccountRegistryForm(FlaskForm):
    company_name = StringField('Company-Name',validators=[Required(), Length(1,64)])
    company_address = StringField('Company-Address', validators=[Required()])
    submit = SubmitField('Register-Account')

    def validate_company_name(self, field):
        if Account.query.filter_by(company_name=field.data).first():
            raise ValidationError(field.data," account already registered.")

class OpportunityRegistryForm(FlaskForm):
    position_name = StringField('Position-Name',validators=[Required(), Length(1,64)])
    no_of_positions = StringField('number of postions', validators=[Required()])
    submit = SubmitField('Post')

    def validate_position_name(self, field):
        pass

class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(field.data,"name already registered")

class EditprofileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    role = SelectField('Role', coerce=int)
    about_me = TextAreaField('About Me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email alraedy Registered.')


    def validate_username(self, field):
        if field.data  != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')



    
