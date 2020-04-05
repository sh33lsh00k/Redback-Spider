from datetime import datetime
from flaskApp import db, login_manager
from flask_login import UserMixin
from sqlalchemy import *


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id 			= db.Column(db.Integer, primary_key=True)
	username 	= db.Column(db.String(25), unique=True, nullable=False)
	email 		= db.Column(db.String(125), unique=True, nullable=False)
	image 		= db.Column(db.String(20), nullable=False, default='default.jpg')
	password 	= db.Column(db.String(100), nullable=False)
	# posts 		= db.relationship('Post', backref='author', lazy=True)

	def __repr__(self):
		return f"User('{self.username}', Email('{self.email}', Password('{self.image}')"

class APIFromJSLinks(db.Model):
	id 					= db.Column(db.Integer, primary_key=True)
	userId 				= db.Column(db.Integer, ForeignKey(User.id), nullable=False)
	crawler 			= db.Column(db.String(100), unique=False, nullable=False)
	JSLink    	  		= db.Column(db.Text, unique=False, nullable=False)
	JSLinkHash 	  		= db.Column(db.String(200), unique=False, nullable=False)
	JSLinkHTML 	  		= db.Column(db.Text, unique=False, nullable=False)
	APIcontext    		= db.Column(db.Text, unique=False, nullable=False)
	dateTime 			= db.Column(db.String(100), unique=False, nullable=False)


class CrawledEndpoints(db.Model):
	id 					= db.Column(db.Integer, primary_key=True)
	userId 				= db.Column(db.Integer, ForeignKey(User.id), nullable=False)
	crawler 			= db.Column(db.String(100), unique=False, nullable=False)
	crawledEndpoints	= db.Column(db.Text, unique=False, nullable=False)


class BlacklistJSLinks(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	userId 			= db.Column(db.Integer, ForeignKey(User.id), nullable=False)
	JSLink    	  	= db.Column(db.Text, unique=False, nullable=False)


# blacklisting APIs that found during crawling like: image/png, application/json etc
class BlacklistAPI(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	userId 			= db.Column(db.Integer, ForeignKey(User.id), nullable=False)
	API     	  	= db.Column(db.Text, unique=False, nullable=False)
	domainName 		= db.Column(db.String(100), unique=False, nullable=False)
