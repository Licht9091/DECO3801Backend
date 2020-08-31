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

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    description = db.Column(db.String(255))
    value = db.Column(db.Float)
    category = db.Column(db.String(255))
    goal = db.Column(db.Integer, primary_key=True)
    goalContrabution = db.Column(db.Float)


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    goalStartDate = db.Column(db.DateTime)
    goalEndDate = db.Column(db.DateTime)
    goalAmount = db.Column(db.Integer)
    totalContrabution = db.Column(db.Float)


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


import json
import numpy as np
import string
import random
import pandas as pd
import datetime

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)

bank = pd.read_csv("/home/Benno/DECO3801Backend/Darrens_money.csv")

bank["date"] = pd.to_datetime(bank["date"], format="%d/%m/%Y")
bank = bank.sort_values('date')
bank['money'] = bank['transaction'].cumsum()
catagories = ['entertainment', 'groceries', 'bills', 'uncategorized']
bank['category'] = bank['transaction'].apply(lambda x: catagories[np.random.randint(0,4)])
df = bank.copy()

@app.route("/get_transactions")
def get_transactions():
    all_trans = df
    un = df[df['category']=='uncategorized']
    un_income = un[un['transaction'] > 0]
    un_expense = un[un['transaction'] < 0]

    all_trans_list = []
    for ix, row in all_trans.iterrows():
        transaction = {
            "id": ''.join(random.choice(string.ascii_lowercase) for x in range(10)),
            "date": row['date'],
            "description": row['description'],
            "value": row['money'],
            "category": row['category'],
            #"Goal": goals[random.randint(0,9)],
            #"Goal_contrabution":
        }
        all_trans_list.append(transaction)

    income_trans_list = []
    for ix, row in un_income.iterrows():
        transaction = {
            "id": ''.join(random.choice(string.ascii_lowercase) for x in range(10)),
            "date": row['date'],
            "description": row['description'],
            "value": row['money'],
            "category": row['category'],
            "goal": row['goal'],
            "Goal_contrabution": row['goal_contrabution']
        }
        income_trans_list.append(transaction)

    expense_trans_list = []
    for ix, row in un_expense.iterrows():
        transaction = {
            "id": ''.join(random.choice(string.ascii_lowercase) for x in range(10)),
            "date": row['date'],
            "description": row['description'],
            "value": row['money'],
            "category": row['category'],
            "goal": row['goal'],
            "Goal_contrabution": row['goal_contrabution']
        }
        expense_trans_list.append(transaction)
    fin_dict = {
        "all_transactions": all_trans_list,
        "uncategorized_income": income_trans_list,
        "uncategorized_expense": expense_trans_list
    }
    return json.dumps(fin_dict , indent=5, default=date_handler)




@app.route("/transaction_stats")
def transaction_stats():
    total_money = df['money'].iloc[-1]

    un = df[df['category']=='uncategorized']
    un_total = un['transaction'].shape[0]
    un_spending = un[un['transaction'] < 0]['transaction'].shape[0]
    un_income = un[un['transaction'] > 0]['transaction'].shape[0]

    spending = df[df['transaction'] < 0]['transaction'].sum()
    income = df[df['transaction'] > 0]['transaction'].sum()

    spending = {
        "total": spending
    }
    for cat in df['category'].unique().tolist():
        spend = df[df['category']==cat]['transaction'].sum()
        spending[cat] = round(spend,2)

    week_changes = list(df.groupby(pd.Grouper(key='date', freq='W-MON'))['transaction'].sum().reset_index().sort_values('date')['transaction'].values)
    #print(df)
    week_changes = [round(i, 2) for i in week_changes]


    data_dict = {
        "total-assets": np.random.randint(7000,9000),
        "total-cash": round(total_money, 2),
        "spending-amount": np.random.randint(300,3000),
        "days-till-pay": np.random.randint(1, 14),
        "uncategorised": {
            "total": round(un_total, 2),
            "income": round(un_income, 2),
            "spending": round(un_spending,2)
        },
        "spending": spending,
        "graphable-total-cash": week_changes #[100, 120, 140, 90]
    }
    return data_dict

@app.route("/set_goal")
def set_goal():
    #Set a single goal
    #db.session.add(variable_name)
    #db.session.commit()
    return 200

@app.route("/goal_status")
def goal_status():
    #COMPLETELY RANDOM
    data_dict = {
        "goals": [
            {
                "name": "Rainy Day Fund",
                "goal-value": 1000,
                "current-contribution":np.random.randint(1000, 2000)
            },
            {
                "name": "Overeas Trip",
                "goal-value": 5000,
                "current-contribution":np.random.randint(0, 5000)
            },
            {
                "name": "Overeas Trip",
                "goal-value": 2000,
                "current-contribution":np.random.randint(0, 2000)
            }]
    }

    result = json.dumps(data_dict, indent=5)

    return result





