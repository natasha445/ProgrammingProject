from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
import os
import shutil

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bookstore'

mysql = MySQL(app)

app.secret_key = "myKey"

@app.route("/")
def index():
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM classicBooks"
    myCursor.execute(sqlQuery)
    classicBooks = myCursor.fetchall()
    myCursor.close()
    #renderizar layout
    return render_template('index.html', classicBooks = classicBooks) #menu = menu

@app.route("/contact/")
def contact():
    return render_template('contact.html')

@app.route("/adminPage/")
def adminPage():
    return render_template('adminPage.html')

@app.route("/bookSection/<section>")
def bookSection(section):
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM sectionBooks WHERE BookSection = '{section}'"
    myCursor.execute(sqlQuery)
    bestBooks = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM sectionAuthors WHERE Section = '{section}'"
    myCursor.execute(sqlQuery)
    authors = myCursor.fetchall()
    myCursor.close()

    return render_template('bookSection.html', bestBooks = bestBooks, authors = authors, section = section)

@app.route("/authorBooks/<name>")
def authorBooks(name):
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM authorBooks WHERE Author = '{name}'"
    myCursor.execute(sqlQuery)
    authorBooksInfo = myCursor.fetchall()
    myCursor.close()

    for authorInfo in authorBooksInfo:
        authorImage = authorInfo[7]
        authorDescription = authorInfo[8]
        authorDate = authorInfo[9]

    return render_template('authorBooks.html', authorBooksInfo = authorBooksInfo, authorImage = authorImage, authorDescription = authorDescription, authorDate = authorDate)

@app.route("/requestBookInfo/", methods=['POST'])
def requestBookInfo():
    if request.method == "POST":
        name = request.form['userName']
        email = request.form['userEmail']
        bookName = request.form['bookName']
        bookAuthor = request.form['bookAuthor']
        
        myCursor = mysql.connection.cursor()
        myCursor.execute("INSERT INTO requests (Name, Email, BookName, BookAuthor) VALUES (%s, %s, %s, %s)", (name, email, bookName, bookAuthor))
        mysql.connection.commit()

        myCursor.close()

    return redirect(url_for('contact'))

@app.route("/adminLogin/")
def adminLogin():
    return render_template('adminLogin.html')

@app.route("/userLogin/", methods=['POST'])
def userLogin():
    if request.method == "POST":
        name = request.form['userName']
        password = request.form['userPassword']
        
        myCursor = mysql.connection.cursor()
        myCursor.execute("SELECT UserValidation (%s, %s)", (name, password))
        functionResult = myCursor.fetchall()
        myCursor.close()

        for result in functionResult:
            validCredentials = result[0]

        if validCredentials == 0:
            flash('The credentials are invalid or user is not active.')
            return redirect(url_for('adminLogin'))

    return redirect(url_for('adminPage'))

@app.route("/submitNewBook/", methods=['POST'])
def submitNewBook():
    if request.method == "POST":
        bookTitle = request.form['bookTitle']
        bookAuthor = request.form['bookAuthor']
        bookSection = request.form['bookSection']
        bookType = request.form['bookType']
        bookYear = int(request.form['bookYear'])
        bookDownloadUrl = request.form['bookDownloadUrl']
        isBestBook = int(request.form['bestBook'])
        isClassicBook = int(request.form['classicBook'])
        bookImagePath = request.form['bookImageSrc']
        bookDescription = request.form['bookDescription']

        bookImage = bookImagePath.split(os.sep)
        bookImageSrc = '/static/images/' + bookImage[-1]
        
        bookExists = checkIfBookExists(bookTitle)
        authorExists = checkIfAuthorExists(bookAuthor)

        if bookExists == 1:
            flash('Book already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertBooks'))
        else:
            if authorExists == 0:
                flash('The author does not exists on Data Base, the book was not added')
                return redirect(url_for('adminContent', type = 'insertBooks'))
            else:
                #validar que el autor elegido y la seccion coincidan con los datos del input (seccion)
                #implementar el acortador de URL
                myCursor = mysql.connection.cursor()
                myCursor.execute("INSERT INTO books (Title, Author, Year, DownloadUrl, BookTooltip, BookSection, IsActive, Type, BookImage, IsBestBook, IsClassicBook)" +
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (bookTitle, bookAuthor, bookYear, bookDownloadUrl, bookDescription, bookSection, 1, bookType, 
                    bookImageSrc, isBestBook, isClassicBook))
                mysql.connection.commit()
                myCursor.close()

                moveBookCoverImageToFolder(bookImage[-1])

    return redirect(url_for('adminPage'))

@app.route("/submitNewUser/", methods=['POST'])
def submitNewUser():
    if request.method == "POST":
        userName = request.form['userName']
        userPassword = request.form['userPassword']

        userExists = checkIfUserExists(userName)

        if userExists == 1:
            flash('User already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertUsers'))
        else:
            myCursor = mysql.connection.cursor()
            myCursor.execute("INSERT INTO users (UserName, UserPassword, IsActive)" +
                " VALUES (%s, %s, %s)", (userName, userPassword, 1))
            mysql.connection.commit()
            myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/submitNewAuthor/", methods=['POST'])
def submitNewAuthor():
    if request.method == "POST":
        authorName = request.form['authorName']
        authorSection = request.form['authorSection']
        authorDate = request.form['authorDate']
        authorImagePath = request.form['authorImageSrc']
        authorDescription = request.form['authorDescription']

        authorImage = authorImagePath.split(os.sep)
        authorImageSrc = '/static/images/' + authorImage[-1]
        
        authorExists = checkIfAuthorExists(authorName)

        if authorExists == 1:
            flash('Author already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertAuthors'))
        else:
            myCursor = mysql.connection.cursor()
            myCursor.execute("INSERT INTO authors (Name, IsActive, Section, Description, AuthorImage, BirthDeathDate)" +
                " VALUES (%s, %s, %s, %s, %s, %s)", (authorName, 1, authorSection, authorDescription, authorImageSrc, authorDate))
            mysql.connection.commit()
            myCursor.close()

            moveAuthorImageToFolder(authorImage[-1])

    return redirect(url_for('adminPage'))

@app.route("/deactivateBook/", methods=['POST'])
def deactivateBook():
    if request.method == "POST":
        bookTitle = request.form['bookTitle']

        bookExists = checkIfBookExists(bookTitle)

        if bookExists == 0:
            flash('Book does not exists on Data Base')
            return redirect(url_for('adminContent', type = 'deactivateBooks'))
        else:
            myCursor = mysql.connection.cursor()
            sqlQuery = "UPDATE books SET IsActive = 0 WHERE Title = %s"
            myCursor.execute(sqlQuery, (bookTitle,))
            mysql.connection.commit()
            myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/deactivateUser/", methods=['POST'])
def deactivateUser():
    if request.method == "POST":
        userName = request.form['userName']

        userExists = checkIfUserExists(userName)

        if userExists == 0:
            flash('User does not exists on Data Base')
            return redirect(url_for('adminContent', type = 'deactivateUsers'))
        else:
            myCursor = mysql.connection.cursor()
            sqlQuery = "UPDATE users SET IsActive = 0 WHERE UserName = %s"
            myCursor.execute(sqlQuery, (userName,))
            mysql.connection.commit()
            myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/deactivateAuthor/", methods=['POST'])
def deactivateAuthor():
    if request.method == "POST":
        authorName = request.form['authorName']

        authorExists = checkIfAuthorExists(authorName)

        if authorExists == 0:
            flash('Author does not exists on Data Base')
            return redirect(url_for('adminContent', type = 'deactivateAuthors'))
        else:
            myCursor = mysql.connection.cursor()
            sqlQuery = "UPDATE authors SET IsActive = 0 WHERE Name = %s"
            myCursor.execute(sqlQuery, (authorName,))
            mysql.connection.commit()
            myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/updateUser/", methods=['POST'])
def updateUser():
    if request.method == "POST":
        userName = request.form['userName']

        userExists = checkIfUserExists(userName)

        if userExists == 0:
            flash('User does not exists on Data Base')
            return redirect(url_for('adminContent', type = 'updateUsers'))
        else:
            myCursor = mysql.connection.cursor()
            sqlQuery = f"SELECT * FROM usersView WHERE UserName = '{userName}'"
            myCursor.execute(sqlQuery)
            userInfo = myCursor.fetchall()
            myCursor.close()

    return render_template('updateUserInfo.html', userInfo = userInfo, userName = userName)

@app.route("/sendUpdatedUserInfo/<user>", methods=['POST'])
def sendUpdatedUserInfo(user):
    #validar que el nuevo nombre de usuario no coincida con uno que exista en la tabla
    if request.method == "POST":
        userName = request.form['userName']
        userPassword = request.form['userPassword']
        userActive = request.form['userActive']

        myCursor = mysql.connection.cursor()
        sqlQuery = "UPDATE users SET UserName = %s, userPassword = %s, IsActive = %s WHERE UserName = %s"
        myCursor.execute(sqlQuery, (userName, userPassword, userActive, user))
        mysql.connection.commit()
        myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/updateBook/", methods=['POST']) #TO DO
def updateBook():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/updateAuthor/", methods=['POST']) #TO DO
def updateAuthor():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllUsers/", methods=['POST']) #TO DO
def listAllUsers():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllBooks/", methods=['POST']) #TO DO
def listAllBooks():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllAuthors/", methods=['POST']) #TO DO
def listAllAuthors():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllRequests/", methods=['POST']) #TO DO
def listAllRequests():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/adminContent/<type>")
def adminContent(type):
    #SELECT DE TODAS LAS TABLAS (USER, BOOKS, AUTHORS Y REQUEST)
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM usersView"
    myCursor.execute(sqlQuery)
    userTableInfo = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM requestsView"
    myCursor.execute(sqlQuery)
    requestTableInfo = myCursor.fetchall()
    myCursor.close()

    return render_template('adminContent.html', type = type, usersTableInfo = userTableInfo, requestTableInfo = requestTableInfo)

def checkIfBookExists(bookTitle):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT BookExists (%s)", (bookTitle,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        bookExists = result[0]

    myCursor.close()
    return bookExists

def checkIfAuthorExists(authorName):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT AuthorExists (%s)", (authorName,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        authorExists = result[0]

    myCursor.close()
    return authorExists

def checkIfUserExists(userName):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT UserExists (%s)", (userName,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        userExists = result[0]

    myCursor.close()
    return userExists

def moveBookCoverImageToFolder(file):
    source = 'C:/Users/Natasha.Mora/Downloads/' + file
    destination = 'C:/Users/Natasha.Mora/Documents/Repos/ProgrammingProject/static/images'

    shutil.move(source, destination)

def moveAuthorImageToFolder(file):
    source = 'C:/Users/Natasha.Mora/Downloads/' + file
    destination = 'C:/Users/Natasha.Mora/Documents/Repos/ProgrammingProject/static/images/authors'

    shutil.move(source, destination)

if __name__ == "__main__":
    app.run(port=5500, debug=True)