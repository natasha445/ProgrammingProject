from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
import os

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
    return render_template('index.html', classicBooks = classicBooks)

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
        
        myCursor = mysql.connection.cursor()
        myCursor.execute("SELECT BookExists (%s)", (bookTitle,))
        functionResult = myCursor.fetchall()

        for result in functionResult:
            bookExists = result[0]

        if bookExists == 1:
            flash('Book already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertBooks'))
        else:
            myCursor.execute("INSERT INTO books (Title, Author, Year, DownloadUrl, BookTooltip, BookSection, IsActive, Type, BookImage, IsBestBook, IsClassicBook)" +
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (bookTitle, bookAuthor, bookYear, bookDownloadUrl, bookDescription, bookSection, 1, bookType, 
            bookImageSrc, isBestBook, isClassicBook))
            mysql.connection.commit()

        myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/submitNewUser/", methods=['POST'])
def submitNewUser():
    if request.method == "POST":
        userName = request.form['userName']
        userPassword = request.form['userPassword']
        
        myCursor = mysql.connection.cursor()
        myCursor.execute("SELECT UserExists (%s)", (userName,))
        functionResult = myCursor.fetchall()

        for result in functionResult:
            userExists = result[0]

        if userExists == 1:
            flash('User already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertUsers'))
        else:
            myCursor.execute("INSERT INTO users (UserName, UserPassword, IsActive)" +
            " VALUES (%s, %s, %s)", (userName, userPassword, 1))
            mysql.connection.commit()

        myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/deactivateBook/", methods=['POST'])
def deactivateBook():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/deactivateUser/", methods=['POST'])
def deactivateUser():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/updateUser/", methods=['POST'])
def updateUser():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/updateBook/", methods=['POST'])
def updateBook():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllUsers/", methods=['POST'])
def listAllUsers():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/listAllBooks/", methods=['POST'])
def listAllBooks():
    if request.method == "POST":
        print("xcvx")

    return redirect(url_for('adminPage'))

@app.route("/adminContent/<type>")
def adminContent(type):
    return render_template('adminContent.html', type = type)

if __name__ == "__main__":
    app.run(port=5500, debug=True)