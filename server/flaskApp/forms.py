from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskApp.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
	username 	= StringField('Username', validators=[DataRequired(), Length(min=5, max=25)])
	email 		= StringField('Email', validators=[DataRequired(), Email()])
	password 	= PasswordField('Password', validators=[DataRequired(), Length(min=8, max=100)])
	confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=100), EqualTo('password')])
	submit 		= SubmitField('Sign Up')

	def validate_username(self, username):
		user 	= User.query.filter_by(username=username.data).first()
		if user: raise ValidationError('That username already exists!')

	def validate_email(self, email):
		email 	= User.query.filter_by(email=email.data).first()
		if email: raise ValidationError('That username already exists!')

class LoginForm(FlaskForm):
	email 		= StringField('Email', validators=[DataRequired(), Email()])
	password 	= PasswordField('Password', validators=[DataRequired(), Length(min=8, max=100)])
	remember 	= BooleanField('Remember me')
	submit 		= SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	username 	= StringField('Username', validators=[DataRequired(), Length(min=5, max=25)])
	email 		= StringField('Email', validators=[DataRequired(), Email()])
	picture 	= FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit 		= SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user 	= User.query.filter_by(username=username.data).first()
			if user: raise ValidationError('That username already exists!')

	def validate_email(self, email):
		if email.data != current_user.email:
			email 	= User.query.filter_by(email=email.data).first()
			if email: raise ValidationError('That username already exists!')