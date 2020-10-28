from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_app import db

# User table
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    passwordHash = db.Column(db.String(255))
    registerDate = db.Column(db.DateTime, default=datetime.now)
    periodStart = db.Column(db.DateTime, default=datetime.now)
    spendingAmount = db.Column(db.Float)
    bankAccountId = db.Column(db.Integer, db.ForeignKey('bankaccounts.accountNumber', ondelete='SET NULL'), nullable=True)
    bankAccount = db.relationship('BankAccount', foreign_keys=bankAccountId)

    def check_password(self, password):
            return check_password_hash(self.passwordHash, password)

    # This NEEDS to be implemented for login_user to work (God I nearly pulled my hair out debugging this one)
    def get_id(self):
        return self.username

class BankAccount(db.Model):
    __tablename__ = "bankaccounts"

    accountNumber = db.Column(db.Integer, primary_key=True)
    bankId = db.Column(db.Integer, db.ForeignKey('banks.bsb', ondelete='SET NULL'))
    accountName = db.Column(db.String(255))
    bank = db.relationship('Bank', foreign_keys=bankId)

class Bank(db.Model):
    __tablename__ = "banks"

    bsb = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user = db.relationship('User', foreign_keys=userId)
    date = db.Column(db.DateTime)
    description = db.Column(db.String(255))
    value = db.Column(db.Float)
    category = db.Column(db.String(255))
    goalId = db.Column(db.Integer, db.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True)
    goal = db.relationship('Goal', foreign_keys=goalId)


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user = db.relationship('User', foreign_keys=userId)
    goalStartDate = db.Column(db.DateTime)
    goalEndDate = db.Column(db.DateTime)
    goalAmount = db.Column(db.Float)
    totalContribution = db.Column(db.Float)
    fortnightlyContribution = db.Column(db.Float)
    description = db.Column(db.String(255), default=0.0)

class Category(db.Model):
    _tablename_ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    catagoryName = db.Column(db.String(255))

class TransactionCategories(db.Model):
    _tablename_ = "transactioncategories"

    id = db.Column(db.Integer, primary_key=True)
    transactionId = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True)
    transaction = db.relationship('Transaction', foreign_keys=transactionId)
    goalId = db.Column(db.Integer, db.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True)
    goal = db.relationship('Goal', foreign_keys=goalId)
    ammount = db.Column(db.Float)

class BudgetItems(db.Model):
    _tablename_ = "budgetitems"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user = db.relationship('User', foreign_keys=userId)
    name = db.Column(db.String(255))
    ammount = db.Column(db.Float)
    tag = db.Column(db.String(255))