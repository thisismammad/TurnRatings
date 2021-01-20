from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "6d62e6dcc63c1a394af6745eb118b4ab1"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///DataBase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

from app import routes
