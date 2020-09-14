from flask_app import db, app, login_manager
from sql_tables import *
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask import Flask, redirect, render_template, request, url_for

@login_manager.user_loader
def load_user(user):
    return User.query.filter_by(username=user).first()

# Entry Endpoint
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    if request.method == "GET": return ''
    if current_user.is_authenticated: return 'Successfully logged in!'

    user = load_user(request.form["username"])
    if user is None: return 'User does not exist'

    if not user.check_password(request.form["password"]): return 'Wrong password'

    login_user(user)
    return 'Successfully logged in!'

# This logs you out if you are logged in.
@app.route("/logout")
@login_required
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

def hash_string(s):
    return round(int(hashlib.md5(str.encode(s)).hexdigest(),16)/10000000000000000000000000000000)

#userid aint working.

#current_user.id
@app.route("/get_transactions")
@login_required
def get_transactions():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

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
@login_required
def transaction_stats():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

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

    allCategories = [i.catagoryName for i in Category.query.all()]

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
        "all-categories": allCategories,
        "graphable-total-cash": week_changes #[100, 120, 140, 90]
    }
    return data_dict

#https://benno.pythonanywhere.com/set_goal?description=HOLIDAY&goalAmount=3000&endDate=01-01-2025
@app.route("/set_goal")
@login_required
def set_goal():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

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
        return json.dumps({"success": 200, "id": goalid}, indent=5)
    except:
        return json.dumps({"success": 400}, indent=5)

@app.route("/delete_goal")
@login_required
def delete_goal():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

    goalId = request.args.get('id', type = str)
    goal = Goal.query.filter_by(id=goalId).first()

    if (goal == None): return '{"message": "Goal was not found"}'
    db.session.delete(goal)
    db.session.commit()

    return '{"message": "Success"}'

#https://benno.pythonanywhere.com/goal_status?userid=33103738
@app.route("/goal_status")
@login_required
def goal_status():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

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
@login_required
def contribute_to_goal():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

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

@app.route("/add_category")
@login_required
def add_category():
    cName = request.args.get('category', type = str)
    exists = Category.query.filer_by(catagoryName=cName)

    if (exists != None): return '{"message": "Already exists"}'

    c = Category(catagoryName=cName)
    db.session.add(c)
    db.session.commit()

    return '{"message": "Success"}'

#https://benno.pythonanywhere.com/categorize_transaction?transactionid=1&category=entertainment
@app.route("/categorize_transaction")
@login_required
def categorize_transaction():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing

    transid = request.args.get('transactionid', type = int)
    newCat = request.args.get('category', type = str)

    try:
        #trans = Transaction.query.filter_by(id=transid, userId=userid).first()
        trans = Transaction.query.get(transid)
        #print(goal.totalContribution)
        trans.category = newCat
        db.session.commit()
        return json.dumps({"status": "Updated"}, indent=5)
    except:
        return json.dumps({"status": 400}, indent=5)

@app.route("/allocate_transaction")
@login_required
def allocate_transaction():
    userid = current_user.id
    #userid = hash_string("test") # Use this when testing
    """
    transid = request.args.get('transactionid', type = int)
    newCat = request.args.get('category', type = int)

    query = Transaction.query.filter_by(id=transid, userId=userid).all()
    trans = Transaction.query.get(transid)
    #print(goal.totalContribution)
    trans.category = newCat
    db.session.commit()
    """
