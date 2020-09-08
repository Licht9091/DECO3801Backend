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
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', foreign_keys=userId)
    date = db.Column(db.DateTime)
    description = db.Column(db.String(255))
    value = db.Column(db.Float)
    category = db.Column(db.String(255))
    goalId = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)
    goal = db.relationship('Goal', foreign_keys=goalId)


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', foreign_keys=userId)
    goalStartDate = db.Column(db.DateTime)
    goalEndDate = db.Column(db.DateTime)
    goalAmount = db.Column(db.Integer)
    totalContribution = db.Column(db.Float)


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
@app.route("/login")#, methods=["POST"])
def login():
    #if request.method == "GET": return ''

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
import os
import hashlib

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)



"""
#THIS GETS DATA FROM CSV FOR OLD CODE

bank = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + "/Darrens_money.csv")

bank["date"] = pd.to_datetime(bank["date"], format="%d/%m/%Y")
bank = bank.sort_values('date')
bank['money'] = bank['transaction'].cumsum()
catagories = ['entertainment', 'groceries', 'bills', 'uncategorized']
#bank['category'] = bank['transaction'].apply(lambda x: catagories[np.random.randint(0,4)])
bank['category']=bank['transaction'].apply(lambda x: catagories[np.random.randint(0,4)] if x < 0 else catagories[3])
df = bank.copy()
#print(df.head())
"""

def hash_string(s):
    return round(int(hashlib.md5(str.encode(s)).hexdigest(),16)/10000000000000000000000000000000)


def add_csv_to_db():
    userid = hash_string("Darren_test")

    for ix, row in df.iterrows():
        goalid = hash_string("None")
        if row['goal'] == row['goal']: goalid = hash_string(row['goal'])

        tran = Transaction(
            id=ix,
            userId=userid,
            date=row['date'],
            description=row['description'],
            value=row['transaction'],
            category=row['category'] ,
            goalId=goalid)

        db.session.add(tran)
    db.session.commit()
    return "Completed"

#print(Transaction.query.delete())
#print(add_csv_to_db())


#userid aint working.

#current_user.id
@app.route("/get_transactions")
def get_transactions():
    userid = hash_string("Darren_test")#current_user.id
    query = Transaction.query.filter_by(userId=userid)
    df = pd.read_sql(query.statement, query.session.bind)

    print("SQLDB\n", df.head())
    #print("\n", all_trans.columns)

    un = df[df['category']=='uncategorized']
    un_income = un[un['value'] > 0]
    un_expense = un[un['value'] < 0]

    all_trans_list = []
    for ix, row in df.iterrows():
        transaction = {
            "id": row['id'],
            "date": row['date'],
            "description": row['description'],
            "value": row['value'],
            "category": row['category'],

        }
        all_trans_list.append(transaction)

    income_trans_list = []
    for ix, row in un_income.iterrows():
        transaction = {
            "id": row['id'],
            "date": row['date'],
            "description": row['description'],
            "value": row['value'],
            "category": row['category'],
            "goal": row['goalId']
        }
        income_trans_list.append(transaction)

    expense_trans_list = []
    for ix, row in un_expense.iterrows():
        transaction = {
            "id": row['id'],
            "date": row['date'],
            "description": row['description'],
            "value": row['value'],
            "category": row['category'],
            "goal": row['goalId']
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
    userid = hash_string("Darren_test")#current_user.id

    query = Transaction.query.filter_by(userId=userid)
    df = pd.read_sql(query.statement, query.session.bind)

    df['money'] = df['value'].cumsum()
    total_money = df['money'].iloc[-1]

    un = df[df['category']=='uncategorized']
    un_total = un['value'].shape[0]
    un_spending = un[un['value'] < 0]['value'].shape[0]
    un_income = un[un['value'] > 0]['value'].shape[0]

    spending = df[df['value'] < 0]['value'].sum()
    income = df[df['value'] > 0]['value'].sum()

    spending = {
        "total": spending
    }
    for cat in df['category'].unique().tolist():
        spend = df[df['category']==cat]['value'].sum()
        spending[cat] = round(spend,2)

    recent_df =  df[df['date'] >= np.datetime64('now')- np.timedelta64(14,'D')]
    recentSpending = {
        "total": recent_df[recent_df['value'] < 0]['value'].sum()
    }
    print(recent_df.shape, df.shape)
    for cat in recent_df['category'].unique().tolist():
        spend = recent_df[recent_df['category']==cat]['value'].sum()
        recentSpending[cat] = round(spend,2)

    week_changes = list(df.groupby(pd.Grouper(key='date', freq='W-MON'))['value'].sum().reset_index().sort_values('date')['value'].values)
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
        "recent-spending": recentSpending,
        "graphable-total-cash": week_changes #[100, 120, 140, 90]
    }
    return data_dict


transaction_stats()


#https://benno.pythonanywhere.com/set_goal?description=HOLIDAY&goalAmount=3000&endDate=01-01-2025
@app.route("/set_goal")
def set_goal():
    userid = hash_string("Darren_goal_test_2")

    goal_text = request.args.get('description', type = str)
    goalAmount = request.args.get('goalAmount', type = int)
    try:
        endDate = request.args.get('endDate', type = str)
        endDate = datetime.datetime.strptime(endDate, '%d-%m-%Y')
    except:
        endDate = datetime.datetime.strptime("1-01-2030", '%d-%m-%Y')

    goalid = hash_string(goal_text)

    try:
        goal = Goal(id=goalid , userId=userid, description=goal_text, goalAmount=goalAmount, totalContribution=0, goalStartDate=datetime.datetime.now(), goalEndDate=endDate)
        db.session.add(goal)
        db.session.commit()
        return json.dumps({"success": 200}, indent=5)
    except:
        return json.dumps({"success": 400}, indent=5)

#https://benno.pythonanywhere.com/goal_status?userid=33103738
@app.route("/goal_status")
def goal_status():
    userid = hash_string("Darren_goal_test_2")
    try:
        query = Goal.query.filter_by(userId=userid).all()
        #
        #DO THE GOAL STRING

        arr = []
        for g in query:
            if g.goalStartDate is not None:
                sDate = g.goalStartDate.strftime("%d-%m-%Y")
            else:
                sDate = None
            if g.goalEndDate is not None:
                eDate = g.goalEndDate.strftime("%d-%m-%Y")
            else:
                eDate = None
            d = {
                    "description": g.description,
                    "id": g.id,
                    "startDate": sDate,
                    "endDate": eDate,
                    "goal-value": g.goalAmount,
                    "current-contribution": g.totalContribution
                }
            arr.append(d)

        data_dict = {
            "goals": arr
        }

        result = json.dumps(data_dict, indent=5)

        return result
    except Exception as e:
        return json.dumps({"success": 400, "error":str(e)}, indent=5)

#https://benno.pythonanywhere.com/contribute_to_goal?goalid=12493741&contrabution=62.3
@app.route("/contribute_to_goal")
def contribute_to_goal():
    userid = hash_string("Darren_goal_test_2")

    goalid = request.args.get('goalid', type = int)
    contrabution = request.args.get('contrabution', type = float)
    #goalid = 12493741

    try:
        query = Goal.query.filter_by(id=goalid, userId=userid).all()
        goal = Goal.query.get(goalid )
        #print(goal.totalContribution)
        goal.totalContribution = goal.totalContribution + contrabution
        db.session.commit()

        return json.dumps({"status": "ADDED"}, indent=5)
    except:
        return json.dumps({"status": 400}, indent=5)

#Goal.query.delete()
#contribute_to_goal()

#userid = hash_string("Darren_goal_test_2")
#user =  User(id = userid, username="Darren_goal_test_2")
#db.session.add(user)
#db.session.commit()

@app.route("/get_catagories")
def get_catagories():
    d = {
        "catagories": ['entertainment', 'groceries', 'bills', 'uncategorized']
        }
    return json.dumps(d, indent=5)

@app.route("/set_catagories")
def set_catagories():
    return json.dumps({"status": "NOT IMPLEMENTED YET"}, indent=5)

#https://benno.pythonanywhere.com/categorize_transaction?transactionid=1&category=entertainment
@app.route("/categorize_transaction")
def categorize_transaction():
    userid = hash_string("Darren_goal_test_2")

    transid = request.args.get('transactionid', type = int)
    newCat = request.args.get('category', type = str)
    #transid = 1
    #newCat = "entertainment"

    try:
        #trans = Transaction.query.filter_by(id=transid, userId=userid).first()
        trans = Transaction.query.get(transid)
        #print(goal.totalContribution)
        trans.category = newCat
        db.session.commit()
        return json.dumps({"status": "Updated"}, indent=5)
    except:
        return json.dumps({"status": 400}, indent=5)


#categorize_transaction()

@app.route("/allocate_transaction")
def allocate_transaction():
    userid = hash_string("Darren_goal_test_2")
    """
    transid = request.args.get('transactionid', type = int)
    newCat = request.args.get('category', type = int)

    query = Transaction.query.filter_by(id=transid, userId=userid).all()
    trans = Transaction.query.get(transid)
    #print(goal.totalContribution)
    trans.category = newCat
    db.session.commit()
    """







