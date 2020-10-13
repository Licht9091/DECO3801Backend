# Overview

This is the backend code for our DECO3801 app.

This is python code and uses flask to locally run a server for which the frontend code can connect to.

The server will connect to an AWS that holds the database and all user information that this flask server will serve.

# Installation

1. Clone this repository.
2. Ensure python 3.8 and pip are installed.
3. Create a file called CONFIG.txt in the root directory of the repository clone. (Not commited for security reasons.)
4. Open CONFIG.txt and enter the credentials that the code requires. (Contact developers for this information.)

Run the following commands (Linux):
pip install -r requirements.txt
export FLASK_APP="flask_app.py"
flask run --host=0.0.0.0

The server should now be running on local host and the front end code should now be able to access this backend on local host.
