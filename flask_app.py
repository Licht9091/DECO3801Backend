from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

# User table
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    passwordHash = db.Column(db.String(255))
    registerDate = db.Column(db.DateTime, default=datetime.now)
    bankAccountId = db.Column(db.Integer, db.ForeignKey('bankaccounts.accountNumber'), nullable=True)
    bankAccount = db.relationship('BankAccount', foreign_keys=bankAccountId)

    def check_password(self, password):
            return check_password_hash(self.passwordHash, password)

    # This NEEDS to be implemented for login_user to work (God I nearly pulled my hair out debugging this one)
    def get_id(self):
        return self.username

class BankAccount(db.Model):
    __tablename__ = "bankaccounts"

    accountNumber = db.Column(db.Integer, primary_key=True)
    bankId = db.Column(db.Integer, db.ForeignKey('banks.bsb'))
    accountName = db.Column(db.String(255))
    bank = db.relationship('Bank', foreign_keys=bankId)

class Bank(db.Model):
    __tablename__ = "banks"

    bsb = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user):
    return User.query.filter_by(username=user).first()

# This is an example end point, here you can recieve or return GET/POST requests
# You can also render html and pass it variables from here that can be usalised in
# the HTML to create dynamic webpages.
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# Example of login, the browser caches this stuff and keeps you logged in. Idk how
# it works with an app and react though. We can have this return json or just message
# body, should be able to set response codes and headers and stuff too.
@app.route("/login", methods=["POST"])
def login():
    if request.method == "GET": return ''

    # I think this should be request.data.get("username") unless it is just a form like a webpage response
    user = load_user(request.form["username"])
    if user is None: return 'User does not exist'

    if not user.check_password(request.form["password"]): return 'Wrong password'

    login_user(user)
    return 'Successfully logged in!'

# This logs you out if you are logged in.
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return 'Successfully logged out!'
    else:
        return 'No user was logged in.'

@app.route("/testloggedin")
def testloggedin():
    if current_user.is_authenticated: return 'The user is logged in. ({})'.format(current_user.username)
    else: return 'The user is not logged in.'

@app.route("/whatever")
def helloworld():
    return '{"message": "Hello world"}'