from flask import Flask, render_template
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


#Landing page, default endpoint
@app.route('/')
def index():
    return render_template('index.html')

#Handle sign-in and redirect accordingly
#@app.route('/sign-in', methods=['POST']):
    #def login():



#FUNCTIONS

#Get retrieve username and password from database
def getUserDetails(username):
    return "test"

#Run server
if __name__ == "__name__":
    app.run()