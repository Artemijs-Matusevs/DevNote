from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

#SET UP CONNECTION TO SQLITE DB
DB = 'var/DevNote.db'
conn = sqlite3.connect(DB, check_same_thread=False)
cursor = conn.cursor()


#COLORS FOR THE ALERT MESSAGE
green = "#149886"
red = "#A45D5D"


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
        #print(username, password)

        #Find user in DB
        storedDetails = getUserDetails(username)
        #print(storedDetails)
        if storedDetails: #Check if the details exist
            storedUsername = storedDetails[0]#Get stored username and password
            storedPassword = storedDetails[1]
            #print(storedUsername, storedPassword)

            #Check stored hashed password with provided password
            if bcrypt.check_password_hash(storedPassword, password):
                print("Correct")
            else:
                return render_template('index.html', alertMessage="Sign-in Error: Invalid details", alertColor=red)
                #print("Wrong password")

        else: #If no record found (The tuple is empty)
            #print("Username doesn't exist")
            return render_template('index.html', alertMessage="Sign-in Error: Invalid details", alertColor=red)

    
    #If HTTP Request method isn't POST
    else: # Else redirect to root
        return redirect(url_for('index'))
    

        

#Handle registration and redirect accordingly
@app.route('/register', methods=['GET', 'POST'])
def register():
    #Check the HTTP request method
    if request.method == 'POST':#If POST i.e. being accessed from html form
        #Get details from the registration form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fullName = request.form['fullName']

        #Hash the entered password
        hashedPassword = bcrypt.generate_password_hash(password).decode('utf-8')

        try: #Execute SQL query to INSERT new record to users table
            cursor.execute(''' INSERT INTO users
                           (username, email, password, full_name)
                           VALUES (?, ?, ?, ?)''' , (username, email, hashedPassword, fullName,))
            conn.commit() #Commit the changes to the SQL db
            
            return render_template('index.html', alertMessage="Account has been created", alertColor=green) #Render the index page again with alert message
        
        except sqlite3.Error as error: #Catch any errors

            errorMessage = str(error) #Convert error to string

            #Check error message to see which constraint has been failed
            if (errorMessage == "UNIQUE constraint failed: users.email"):#EMAIL ALREADY EXISTS
                return render_template('index.html', alertMessage="Error creating account: Email already in use", alertColor=red)
            
            elif (errorMessage == "UNIQUE constraint failed: users.username"):#USERNAME ALREADY EXISTS
                return render_template('index.html', alertMessage="Error creating account: username already in use", alertColor=red)
            
            else:#OTHER ERRORS
                print(error)
                return render_template('index.html', alertMessage="Error creating account", alertColor=red)



    else: #HTTP request method wasn't POST, redirect to index.
        return redirect(url_for('index'))


#The user dashboard
@app.route('/dashboard')
def dashboard():
    return None





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


