from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

#SET UP CONNECTION TO SQLITE DB
DB = 'var/DevNote.db'
conn = sqlite3.connect(DB, check_same_thread=False)
cursor = conn.cursor()


#Landing page, default endpoint
@app.route('/')
def index():
    return render_template('index.html')


#Handle sign-in and redirect accordingly
@app.route('/sign-in', methods=['GET', 'POST'])
def login():
    #Check the HTTP request method
    if request.method == 'POST': #If POST i.e. being accessed from html form
        #Get details from sign-in form
        username = request.form['username']
        password = request.form['password']
        print(username, password)

        #Find user in DB
        storedDetails = getUserDetails(username)
        #print(storedDetails)
        if storedDetails: #Check if the details exist
            storedUsername = storedDetails[0]#Get stored username and password
            storedPassword = storedDetails[1]
            print(storedUsername, storedPassword)
        else: #If no record found
            print("Username doesn't exist")

        return redirect(url_for('index'))
    
    else: # Else redirect to root
        return redirect(url_for('index'))
        



#FUNCTIONS

#Get retrieve username and password from database of a specific user
def getUserDetails(username):
    try: #Execute SQL query to get back the password and username, of a specific user
        cursor.execute(''' SELECT username, password
                       FROM users
                       WHERE username = ? ''', (username,))
        
        user_record = cursor.fetchone() #Store as tuple
        return user_record
    
    except sqlite3.Error as error: #Catch any errors
        print("Error occured:", error)
        return None



#TESTING
#print(getUserDetails("timm"))


