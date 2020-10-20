from flask_app import db, app, login_manager
from sql_tables import *
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask import Flask, redirect, render_template, request, url_for

import json
import numpy as np
import string
import random
import pandas as pd
import datetime
import os
import hashlib

"""Handle annoying dates """
date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)

def hash_string(s):
    """Hashes the inputted string - used to create unique id's
    """
    return round(int(hashlib.md5(str.encode(s)).hexdigest(),16)/10000000000000000000000000000000)

@login_manager.user_loader
def load_user(user):
    return User.query.filter_by(username=user).first()

#___________________________
#API ENDPOINTS

# Entry Endpoint
@app.route('/')
def hello_world():
    return 'Hello from Team Diego!'

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    """Logs the user in with the credetials provided
    
    Keyword arguments:
    username -- the users name (should not be None)
    password -- the users password (should not be None)
    """
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
    """Logs the user out"""
    if current_user.is_authenticated:
        logout_user()
        return 'Successfully logged out!'
    else:
        return 'No user was logged in.'

@app.route("/testloggedin")
def testloggedin():
    """Test if a user is logged in

    Returns:
    - logged in username
    """
    if current_user.is_authenticated: return 'The user is logged in. ({})'.format(current_user.username)
    else: return 'The user is not logged in.'

#/get_transactions
@app.route("/get_transactions")
@login_required
def get_transactions():
    """Gets all transactions and sorts them into uncatagoriesed income and expense

    Returns:
    json object -  {
            "all_transactions": list(dicts),
            "uncategorized_income": list(dicts),
            "uncategorized_expense": list(dicts),
        }
    """
    userid = current_user.id

    #access the transaction table
    query = Transaction.query.filter_by(userId=userid)
    df = pd.read_sql(query.statement, query.session.bind)

    #sort out uncatagorised, income and expenses
    un = df[df['category']=='uncategorized']
    un_income = un[un['value'] > 0]
    un_expense = un[un['value'] < 0]

    #turn data into dict
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

    #turn data into dict
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

    #turn data into dict
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

#/transaction_stats
@app.route("/transaction_stats")
@login_required
def transaction_stats():
    """Creates statistics generated from the users transactions

    Returns:
    json object -  {
            "total-assets": int,
            "total-cash": float,
            "spending-amount": int,
            "days-till-pay": int,
            "uncategorised": {
                "total": float,
                "income": float,
                "spending": float
            },
            "spending": float,
            "recent-spending": float,
            "all-categories": float,
            "graphable-total-cash": list(float)
        }
    """
    userid = current_user.id

    #access transaction table
    query = Transaction.query.filter_by(userId=userid)
    df = pd.read_sql(query.statement, query.session.bind)

    #basic transaction calcs
    df['money'] = df['value'].cumsum()
    total_money = df['money'].iloc[-1]

    #split data into smaller catagories of total, spending and income, uncatagorised and catagorised
    un = df[df['category']=='uncategorized']
    un_total = un['value'].shape[0]
    un_spending = un[un['value'] < 0]['value'].shape[0]
    un_income = un[un['value'] > 0]['value'].shape[0]

    spending = df[df['value'] < 0]['value'].sum()
    income = df[df['value'] > 0]['value'].sum()

    spending = {
        "total": spending
    }

    #do some calc for total spending per catagory
    for cat in df['category'].unique().tolist():
        spend = df[df['category']==cat]['value'].sum()
        spending[cat] = round(spend,2)

    #limit spending to most recent spending
    recent_df =  df[df['date'] >= np.datetime64('now')- np.timedelta64(14,'D')]
    recentSpending = {
        "total": recent_df[recent_df['value'] < 0]['value'].sum()
    }

    #prep recent spending to be turned to dict
    for cat in recent_df['category'].unique().tolist():
        spend = recent_df[recent_df['category']==cat]['value'].sum()
        recentSpending[cat] = round(spend,2)

    #transactions ready for graphing
    week_changes = list(df.groupby(pd.Grouper(key='date', freq='W-MON'))['value']
                                            .sum()
                                            .reset_index()
                                            .sort_values('date')['value'].values)
    week_changes = [round(i, 2) for i in week_changes]
    allCategories = [i.catagoryName for i in Category.query.all()]

    #prep for json
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

#/set_goal?description=HOLIDAY&goalAmount=3000&endDate=01-01-2025
@app.route("/set_goal")
@login_required
def set_goal():
    """Saves a goal to the users profile

    Keyword arguments:
    description -- description of the goal (str)
    goalAmount -- goal amount in $ (float)
    fortnightlyGoal -- forntightly contrabution to meet goal by end date (float)

        Optional:
            endDate -- End date to complete the goal by (str)

    Returns:
    status - json object
    """
    #gather function called params
    userid = current_user.id
    goal_text = request.args.get('description', type = str)
    goalAmount = request.args.get('goalAmount', type = float)
    fortnightlyGoal = request.args.get('fortnightlyGoal', type = float)
    try:
        endDate = request.args.get('endDate', type = str)
        endDate = datetime.datetime.strptime(endDate, '%d-%m-%Y')
    except:
        endDate = None

    goalId = hash_string(goal_text) #unique
    try:
        #create the new goal entitiy
        goal = Goal(id=goalId, 
                    userId=userid, 
                    description=goal_text, 
                    goalAmount=goalAmount, 
                    totalContribution=0, 
                    goalStartDate=datetime.datetime.now(), 
                    goalEndDate=endDate, 
                    fortnightlyContribution=fortnightlyGoal)
        db.session.add(goal)
        db.session.commit()
        return json.dumps({"success": 200, , "message": "Success",  "id": goal.id}, indent=5)
    except:
        return json.dumps({"success": 400, "message": "Could not add the Goal"}, indent=5)

@app.route("/delete_goal")
@login_required
def delete_goal():
    """Deletes the defined goal

    Keyword arguments:
    id -- the id of the goal being deleted (str)

    Returns:
    status - json object
    """
    userid = current_user.id
    #gather goal id
    goalId = request.args.get('id', type = str)
    goal = Goal.query.filter_by(id=goalId).first()

    #delete
    if (goal == None): return '{"message": "Goal was not found"}'
    db.session.delete(goal)
    db.session.commit()

    return '{"message": "Success"}'

#/goal_status?userid=33103738
@app.route("/goal_status")
@login_required
def goal_status():
    """Provides the completion status of all current goals

    Returns:
    json object - list(
            { 
                "description": str
                "id": str
                "startDate": str
                "endDate": str
                "goal-value": int
                "fortnightly-contribution": int
                "current-contribution": float
            }
        )
    """
    userid = current_user.id

    try:
        #get Goal table data
        query = Goal.query.filter_by(userId=userid).all()
        TransCats = TransactionCategories.query
        df = pd.read_sql(TransCats.statement, TransCats.session.bind)
        grouped = df.groupby('goalId')
        
        #get the sum of spending/income per goal
        goalSums = {}
        for name, group in grouped:
            goalSums[name] = group['ammount'].sum()

        #prep to turn df into the correct shaped array of dicts for json
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
                    "fortnightly-contribution": g.fortnightlyContribution,
                    "current-contribution": goalSums.get(g.id, 0)#g.totalContribution
                }
            arr.append(d)

        #prep for json
        data_dict = {
            "goals": arr
        }

        result = json.dumps(data_dict, indent=5)

        return result
    except Exception as e:
        return json.dumps({"success": 400, , "message": "Something went wrong, check error message", "error":str(e)}, indent=5)

#/contribute_to_goal?goalid=12493741&contrabution=62.3
@app.route("/contribute_to_goal")
@login_required
def contribute_to_goal():
    """Edit a goals current contrabution amount

    Keyword arguments:
    id -- the id of the goal being edited (str)
    contrabution -- amount to add

    Returns:
    status - json object
    """
    userid = current_user.id

    #get function params
    goalid = request.args.get('goalid', type = int)
    contrabution = request.args.get('contrabution', type = float)

    try:
        #Edit the specified goal
        query = Goal.query.filter_by(id=goalid, userId=userid).all()
        goal = Goal.query.get(goalid)
        goal.totalContribution = goal.totalContribution + contrabution
        db.session.commit()
        return json.dumps({"status": "ADDED"}, indent=5)
    except:
        return json.dumps({"status": 400, "message": "Could not edit the specified goal"}, indent=5)

#/add_category
@app.route("/add_category")
@login_required
def add_category():
    """Adds a catagory to the catagory table

    Keyword arguments:
    catagory -- catagory to be added (str)

    Returns:
    status - json object
    """
    #get function params
    cName = request.args.get('category', type = str)
    exists = Category.query.filer_by(catagoryName=cName)

    #add the catagory
    if (exists != None): return '{"message": "Already exists"}'
    c = Category(catagoryName=cName)
    db.session.add(c)
    db.session.commit()

    return '{"message": "Success"}'

#/categorize_transaction?transactionid=1&category=entertainment
@app.route("/categorize_transaction")
@login_required
def categorize_transaction():
    """Add a catagory to a transaction

    Keyword arguments:
    transactionid -- transaction to be edited
    catagory -- catagory to be added (str)

    Returns:
    status - json object
    """
    userid = current_user.id

    #get function params
    transid = request.args.get('transactionid', type = int)
    newCat = request.args.get('category', type = str)

    try:
        #edit the specified transaction with the new catagory
        trans = Transaction.query.get(transid)
        trans.category = newCat
        db.session.commit()
        return json.dumps({"status": "Updated"}, indent=5)
    except:
        return json.dumps({"status": 400, "message": "Could not edit the specified transaction"}, indent=5)

@app.route("/allocate_transaction", methods=["POST"])
@login_required
def allocate_transaction():
    """Add a goal or multiple to a transaction

    Keyword arguments:
    transid -- transaction to be edited
    goal_arr -- list of goals to be effected with amounts, list(str) 

    Returns:
    status - json object
    """
    userid = current_user.id

    #get function params
    r = request.json
    transid = r['transid']
    goals_arr = r['goals_arr']

    try:
        #add a or multiple goals to a single transaction by adding a or multiple rows to transactioncatagories table
        for contrabution in goals_arr:
            if type(contrabution[0]) != int or type(contrabution[1]) != float:
                return json.dumps({"status": "Bad Request"}, indent=5)
            tcat = TransactionCategories(transactionId=transid, 
                                        goalId=contrabution[0], 
                                        ammount=contrabution[1])
            db.session.add(tcat)
        db.session.commit()
        return json.dumps({"status": 200, "message": "Success"}, indent=5)
    except:
        return json.dumps({"status": 400, "message": "Could not add the required transactioncatagorys to fulfill your request"}, indent=5)


#/get_budget
@app.route("/get_budget")
@login_required
def get_budget():
    """get the active budgets

    Returns:
    json object - {
            "all_budgets": list(
                 {
                    "id": str,
                    "name": str,
                    "fortnightlyAmount": float,
                    "tag": str
                }
            )
        }
    """
    userid = current_user.id

    #get the BudgetItems table
    query = BudgetItems.query.filter_by(userId=userid)
    df = pd.read_sql(query.statement, query.session.bind)

    #prep data from df to array of dicts to be turned into json
    all_budgets_list = []
    for ix, row in df.iterrows():
        budget = {
            "id": row['id'],
            "name": row['name'],
            "fortnightlyAmount": 0 if (row['ammount'] == None) or (math.isnan(row['ammount'])) else row['ammount'],
            "tag": row['tag']
        }
        all_budgets_list.append(budget)

    #prep json
    fin_dict = {
        "all_budgets": all_budgets_list
    }

    return json.dumps(fin_dict , indent=5, default=date_handler)

#/add_budget?name=food&fortAmount=100&tag=yes
@app.route("/add_budget")
@login_required
def add_budget():
    """Create a new budget

    Keyword arguments:
    name -- name of the budget (str)
    fortAmount -- amount to be spent a fortnight (float)
    tag -- honestly not too sure (str)

    Returns:
    status - json object
    """
    userid = current_user.id

    try:
        #gather function params
        name = request.args.get('name', type = str)
        fortAmount = request.args.get('fortAmount', type = float)
        tag = request.args.get('tag', type = str)

        budgetid = hash_string(name+str(userid))
    except:
        return json.dumps({"success": 400, "message": "Failure due to incorrect inputs"}, indent=5)

    try:
        #add a new budget item
        budget = BudgetItems(id=budgetid, 
                    userId=userid, 
                    name=name,
                    ammount=fortAmount,
                    tag=tag)
        db.session.add(budget)
        db.session.commit()
        return json.dumps({"success": 200, "message": "Success", "id": budgetid}, indent=5)
    except:
        return json.dumps({"success": 400, "message": "Could not add the budget"}, indent=5)

#/del_budget?id=8195146
@app.route("/del_budget")
@login_required
def del_budget():
    """Deletes the defined budget

    Keyword arguments:
    id -- the id of the budget being deleted (str)

    Returns:
    status - json object
    """
    userid = current_user.id
    #gather function params
    budgetId = request.args.get('id', type = int)
    budget = BudgetItems.query.filter_by(id=budgetId).first()

    #delete specified budget
    if (budget.userId != userid):  
        return json.dumps({"status": 400, "message": "Invalid ID for user"}, indent=5)
    if (budget == None): 
        return json.dumps({"status": 400, "message": "Budget was not found"}, indent=5)
    db.session.delete(budget)
    db.session.commit()

    return json.dumps({"status": 200, "message": "Success"}, indent=5)

#/edit_budget?id=8195146&&name=newname&fortAmount=101
@app.route("/edit_budget")
@login_required
def edit_budget():
    """Edit the amount to contrabute of the defined budget

    Keyword arguments:
    id -- the id of the budget being edited (str)
    fortAmount -- amount to contrabute each fortnight (float)

    Returns:
    status - json object
    """
    userid = current_user.id

    #gather function params
    budgetid = request.args.get('id', type = int)
    fortAmount = request.args.get('fortAmount', type = float)
    name = request.args.get('name', type = str)

    try:
        #edit the specified budgets fortnightly contrabution 
        budget = BudgetItems.query.filter_by(id=budgetid).first()
        budget.ammount = fortAmount
        budget.name = name
        db.session.commit()

        return json.dumps({"status": 200, "message": "Success"}, indent=5)
    except:
        return json.dumps({"status": 400 , "message": "Could not edit the budget"}, indent=5)


# DEMO STUBS
@app.route("/make_transaction", methods=["POST"])
def make_transaction():
    """Endpoint useful to the Demo """
    if (not current_user.is_authenticated):
        user = load_user("test")
        login_user(user)

    transName = request.values.get('name', type = str)
    amount = request.values.get('amount', type = float)

    transaction = Transaction(id=hash_string(transName + str(datetime.datetime.now())), 
                            userId=current_user.id, 
                            date=datetime.datetime.now(), 
                            description=transName, 
                            value=-amount, 
                            category="Uncategorized")
    db.session.add(transaction)
    db.session.commit()

    return ""