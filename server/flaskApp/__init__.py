from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

"""
Non-Flask Modules => Custom Designed
"""


app = Flask(__name__)
app.config['SECRET_KEY'] = "221aa063a24d8e05a09a3e6395a4e140"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

db 	= SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskApp import routes