from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Init the flask app
app = Flask(__name__)
app.config["DEBUG"] = True

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

# Classes and tables from the db are the same in SQLAlchemy, this is an example
# of what a simple table would look like in python code. Note I didn't actually add
# this table to the database yet though.
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(255))
    lastName = db.Column(db.String(255))


# This is an example end point, here you can recieve or return GET/POST requests
# You can also render html and pass it variables from here that can be usalised in
# the HTML to create dynamic webpages.
@app.route('/')
def hello_world():
    return 'Hello from Flask!'