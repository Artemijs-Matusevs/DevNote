from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from flask_bcrypt import Bcrypt
import sqlite3
import re
from markdown import markdown

app = Flask(__name__)

#SET UP SESSION AND BCRYPT INSTANCE
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
        resetSession()
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
        #Get all books for current user
        books = getBooks(session['user_id'])

        #Get current page content
        rawMarkdown = getPageContent(session['pageId'])
        if(rawMarkdown):
            globalPageContent = markdown(rawMarkdown)

        else:#If no page is present
            globalPageContent = None

        #Render dashboard tempalte
        return render_template('dashboard.html',pageContent=globalPageContent, pageId=session['pageId'], pages=session['pages'], notebookName=session['notebookName'], books=books, bookId=session['bookId'] , pageName=session['pageName'] )

        
    else:#If no user is signed-in
        return redirect(url_for('index'))



#Sign-out 
@app.route('/sign-out')
def signOut():
    #Remove userId from session
    session.pop('user_id', None)
    flash('You have been signed out')

    #Reset all of the session variables
    resetSession()

    return redirect(url_for('index')) #Redirect back to root



#Create new notebook
@app.route('/new-notebook', methods=['POST'])
def newNotebook():
    notebookName = request.form['notebookName']
    userId = session['user_id']
    createNewBook(userId, notebookName)

    return redirect(url_for('dashboard'))



#Create new page
@app.route('/new-page', methods=['POST'])
def newPage():
    pageName = request.form['page_name']
    notebookId = request.form['book_id']
    #print(pageName, notebookId)

    newPage(notebookId, pageName)
    pages = getPages(notebookId)
    session['pages'] = pages

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

    #Reset session
    resetSession()

    #Set the book, pages details within the current session
    session['notebookName'] = notebookName
    session['bookId'] = bookId
    session['pages'] = pages
    session['books'] = books

    #print(pages)
    #print(notebookName, bookId)
    ##return render_template('dashboard.html', pages=pages, notebookName=notebookName, books=books, bookId=bookId)

    return redirect(url_for('dashboard'))

#Open page
@app.route('/open-page', methods=['POST'])
def openPage():
    #Get details of the page
    pageTitle = request.form['page_title']
    pageId = request.form['page_id']


    #Set the active page and content within the current session
    session['pageName'] = pageTitle
    session['pageId'] = pageId

    return redirect(url_for('dashboard'))

    #print(pageTitle, pageId)



#Delete page
@app.route('/delete-page', methods=['POST'])
def delete_page():
    #Get the details of the requested page
    pageId = request.form['page_id']
    bookId = request.form['book_id']
    notebookName = request.form['book_name']

    #Delete the page
    deletePage(pageId)

    #Reset session
    resetSession()

    #Set the new pages
    pages = getPages(bookId)
    session['pages'] = pages
    session['bookId'] = bookId
    session['notebookName'] = notebookName

    #redirect back to dashboard
    return redirect(url_for('dashboard'))

    #print(pageId)


#Delete notebook
@app.route('/delete-notebook', methods=['POST'])
def delete_notebook():
    #Get details of the requested book
    bookId = request.form['delete_book_id']
    print(bookId)

    #First, delete all of the pages of that book
    deleteAllPages(bookId)
    #Delete the book
    deleteNotebook(bookId)

    #Get all the books again
    books = getBooks(session['user_id'])
    resetSession()#Reset current values
    session['books'] = books


    #Redirect back to dashboard
    return redirect(url_for('dashboard'))


#Rename notebook
@app.route('/rename-notebook', methods=['POST'])
def rename_notebook():
    #Get details of new name and notebook ID
    bookId = request.form['bookId']
    newBookName = request.form['newBookName']

    #Run the SQL Query
    renameBook(bookId, newBookName)

    #Refresh all notebooks
    books = getBooks(session['user_id'])
    session['books'] = books
    session['notebookName'] = newBookName

    #redirect to dashboard
    return redirect(url_for('dashboard'))


@app.route('/rename-page', methods=['POST'])
def rename_page():
    #Get details of new page name and page ID
    bookId = request.form['bookId']
    pageId = request.form['pageId']
    newPageName = request.form['newPageName']

    #Run SQL to set new name
    renamePage(pageId, newPageName)

    #Refrest the current pages
    pages = getPages(bookId)
    session['pages'] = pages
    session['pageName'] = newPageName

    #redirect to dashboard
    return redirect(url_for('dashboard'))


#Write to page
@app.route('/write-page', methods=['POST'])
def write_page():
    #Get content details
    data = request.form['ckeditor']
    pageId = request.form['pageId']
    #print(data)

    #Write the data to db
    writeToPage(pageId, data)

    #redirect to dashboard
    return redirect(url_for('dashboard'))


#Export page as MD
@app.route('/export-page', methods=['POST'])
def export_page():
    # Get data
    data = request.form['pageContent']
    pageName = request.form['pageName']
    print("test")

    # Create a response
    response = make_response(data)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename={pageName}.md'

    return response


#Import MD file
@app.route('/import-page', methods=['POST'])
def import_page():
    #Get data
    file = request.files['file']
    pageId = request.form['pageId']

    #Check file extension
    if (file.filename.endswith('.md')):
        rawMarkdown = file.read().decode('utf-8')
        #print(markdownContent)


        #newPageContent = markdown(rawMarkdown)
        newPageContent = markdown(rawMarkdown)

        #Set the new page content
        writeToPage(pageId, newPageContent)

        #redirect to dashboard
        return redirect(url_for('dashboard'))
    else: #Wrong file extension
        return jsonify({'error': 'Only .md extensions are supported'}), 400




#FUNCTIONS
#Function to write to specific page
def writeToPage(pageId, content):
    try:
        cursor.execute('''UPDATE pages
                       SET  page_content = ?
                       WHERE id = ?''', (content, pageId))
        conn.commit()

    except sqlite3.Error as error:
        print("Error occured:", error)
        return None
    
#Function to get content of specific page
def getPageContent(pageId):
    try:
        cursor.execute(''' SELECT page_content
                       FROM pages
                       WHERE id = ?''', (pageId, ))
        page_content = cursor.fetchone() #Store as tuple


        processed_content = page_content[0] if page_content else ""
        #print(processed_content)
        return processed_content
    
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None


#Function to rename a notebook
def renameBook(bookId, newBookName):
    try:
        cursor.execute('''UPDATE notebooks
                       SET  notebook_header = ?
                       WHERE id = ?''', (newBookName, bookId, ))
        conn.commit()
        
    except sqlite3.Error as error:
        print("Error occured:", error)
        return None



#Rename a specific page
def renamePage(pageId, newPageName):
    try:
        cursor.execute(''' UPDATE pages
                       SET page_header = ?
                       WHERE id = ? ''', (newPageName, pageId, ))
        conn.commit()

    except sqlite3.Error as error:
        print("Error has occured:", error)
        return None


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
        cursor.execute(''' SELECT id, notebook_id, page_header
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


#Function to delete a page by pageId
def deletePage(pageId):
    try:
        cursor.execute(''' DELETE FROM pages
                       WHERE id = ? ''', (pageId, ))
        conn.commit()

    except sqlite3.Error as error:
        print("Error has occured: ", error)
        return None


#Function to delete all pages by notebook ID
def deleteAllPages(notebookId):
    try:
        cursor.execute(''' DELETE FROM pages
                       WHERE notebook_id = ?''', (notebookId, ))
        conn.commit()

    except sqlite3.Error as error:
        print("Error: ", error)
        return None


#Function to delete notebook by id
def deleteNotebook(notebookId):
    try:
        cursor.execute(''' DELETE FROM notebooks
                       WHERE id = ?''', (notebookId, ))
        conn.commit()

    except sqlite3.Error as error:
        print("Error :", error)
        return None
    


#Function to reset all session variables
def resetSession():
    #Reset all of the session variables
    session['notebookName'] = None
    session['bookId'] = None
    session['pages'] = None
    session['books'] = None
    session['pageName'] = None
    session['pageId'] = None



#TESTING
#print(getUserDetails("timm"))


