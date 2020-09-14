from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy
from flask_cors import CORS, cross_origin
from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from helper import parse_config


ENV_VARIABLES = parse_config()

# Init the flask app
app = Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config["CORS_HEADERS"] = 'Content-Type'
app.secret_key = ENV_VARIABLES["APP_SECRET"]

print (ENV_VARIABLES["DB_USERNAME"], ENV_VARIABLES["DB_PASSWORD"], ENV_VARIABLES["DB_HOSTNAME"], ENV_VARIABLES["DB_NAME"])

# Database set up stuff
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=ENV_VARIABLES["DB_USERNAME"],
    password=ENV_VARIABLES["DB_PASSWORD"],
    hostname=ENV_VARIABLES["DB_HOSTNAME"],
    databasename=ENV_VARIABLES["DB_NAME"],
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

from url_stubs import *