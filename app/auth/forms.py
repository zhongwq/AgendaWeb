from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
	username = StringField('username', validators=[Required(), Length(1, 30)])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[
		Required(), Length(1, 30), Regexp('^[A-Za-z0-9_.]*$', 0,
										'Usernames must have only letters, '
										'numbers, dots or underscores')])
	password = PasswordField('Password', validators=[
		Required(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[Required()])
	email = StringField('Email', validators=[Required(), Length(1, 60),
											Email()])
	phone = IntegerField('Phone', validators=[Required()])
	submit = SubmitField('Register')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')

class ResetPasswordForm(FlaskForm):
	username = StringField('Input your username', validators=[Required(), Length(1, 30)])
	email = StringField('Input your Email', validators=[Required(), Length(1, 60),
											Email()])
	phone = IntegerField('Input your Phone', validators=[Required(), Length(1,20)])
	submit = SubmitField('Submit')


class verifyPasswordForm(FlaskForm):
	password = PasswordField('Input your password to delete your account', validators=[Required()])
	submit = SubmitField('Delete')