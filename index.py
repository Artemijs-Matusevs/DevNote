from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'DTFn_Ohz_;IK3UqCqu{G>WaWm@lRz%'
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
    #Check if session already exists
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    else:
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
            userId = storedDetails[2]
            #print(userId)

            #Check stored hashed password with provided password
            if bcrypt.check_password_hash(storedPassword, password): #User authenticated
                session['user_id'] = userId #Set the session ID to the user ID
                return redirect(url_for('dashboard'))
                #print("Correct")

            else: # Authentiction failed
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

        #Check password strength
        if checkPasswordStrength(password) == False:
            return render_template('index.html', alertMessage="*Password must be at least 10 characters long, containing lower, upper, special characters and numbers", alertColor=red) #Render the index page again with alert message

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
    if 'user_id' in session:
        books = getBooks(session['user_id'])

        return render_template('dashboard.html', books=books)
    else:
        return redirect(url_for('index'))



#Sign-out 
@app.route('/sign-out')
def signOut():
    #Remove userId from session
    session.pop('user_id', None)
    flash('You have been signed out')
    return redirect(url_for('index')) #Redirect back to root


#Create new notebook
@app.route('/new-notebook', methods=['POST'])
def newNotebook():
    notebookName = request.form['notebookName']
    userId = session['user_id']
    createNewBook(userId, notebookName)

    return redirect(url_for('dashboard'))


#Open book
@app.route('/open-book', methods=['POST'])
def openBook():
    #Get details of the book
    notebookName = request.form['bookTitle']
    bookId = request.form['bookId']

    #Get all of the pages of the clicked book
    pages = getPages(bookId)
    books = getBooks(session['user_id'])

    #print(pages)
    print(notebookName, bookId)
    return render_template('dashboard.html', pages=pages, notebookName=notebookName, books=books)





#FUNCTIONS

#Get retrieve username and password from database of a specific user BY USERNAME
def getUserDetails(username):
    try: #Execute SQL query to get back the password and username, of a specific user
        cursor.execute(''' SELECT username, password, id
                       FROM users
                       WHERE username = ? ''', (username,))
        
        user_record = cursor.fetchone() #Store as tuple
        return user_record
    
    except sqlite3.Error as error: #Catch any errors
        print("Error occured:", error)
        return None


#Retrieve details of specific user by ID
def getUsernameById(userId):
    try:
        cursor.execute(''' SELECT username
                       FROM users
                       WHERE id = ? ''', (userId,))
        
        user_record = cursor.fetchone()
        return user_record
    
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None
    


#Check password complies with strength rules
def checkPasswordStrength(password):
    #Check length
    if len(password) < 10:
        return False
    
    #Check for upper case
    if not re.search(r"[A-Z]", password):
        return False
    
    #Check lower case
    if not re.search(r"[a-z]", password):
        return False
    
    #Check special characters
    if not re.search(r"[!@#$%^&*()\-_=+{}[\]|\:;\"'<>,.?/]", password):
        return False
    
    else:
        return True
    

#Function to create a new notebook taking the userID as a param
def createNewBook(userId, noteBookHeader):
    try:
        cursor.execute(''' INSERT INTO notebooks
                       (user_id, notebook_header)
                       VALUES (?, ?) ''', (userId, noteBookHeader, ))
        conn.commit()
    
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None

#Function to retrieve all books of a specific user by userId
def getBooks(userId):
    try:
        cursor.execute(''' SELECT *
                       FROM notebooks
                       WHERE user_id = ? ''', (userId,))
        
        user_record = cursor.fetchall()
        return user_record
        
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None

#print(getBooks(1))


#Function to get all pages of a specific notebook by notebook ID
def getPages(notebookId):
    try:
        cursor.execute(''' SELECT *
                       FROM pages
                       WHERE notebook_id = ? ''', (notebookId, ))
        
        pages_records = cursor.fetchall()
        return pages_records
    
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None


#Function to create new page in a specific notebook
def newPage(notebookId, pageTitle):
    try:
        cursor.execute(''' INSERT INTO pages
                       (notebook_id, page_header)
                       VALUES (?, ?) ''', (notebookId, pageTitle, ))
        conn.commit()

    except sqlite3.Error as error:
        print("Error occured: ", error)
        return None




#TESTING
#print(getUserDetails("timm"))


