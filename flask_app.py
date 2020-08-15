from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

# Init the flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "fd$5tg(skj23jJl22"

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Database set up stuff
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="PyLicht",
    password="sJ2mnc#cdPz=24G",
    hostname="PyLicht.mysql.pythonanywhere-services.com",
    databasename="PyLicht$backend",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(name):
    return User.query.filter_by(username=name).first()

# Classes and tables from the db are the same in SQLAlchemy, this is an example
# of what a simple table would look like in python code. Note I didn't actually add
# this table to the database yet though.
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    passwordHash = db.Column(db.String(255))
    registerDate = db.Column(db.DateTime, default=datetime.now)
    bankAccountId = db.Column(db.Integer, db.ForeignKey('bankaccounts.accountNumber'), nullable=True)
    bankAccount = db.relationship('BankAccount', foreign_keys=bankAccountId)

    def check_password(self, password):
            return check_password_hash(self.password_hash, password)

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
@login_required
def logout():
    logout_user()
    return 'Successfully logged out!'