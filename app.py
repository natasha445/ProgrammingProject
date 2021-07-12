from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bookstore'

mysql = MySQL(app)

@app.route("/")
def index():
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM books WHERE IsActive = 1 AND IsClassicBook = 1"
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
    sqlQuery = f"SELECT * FROM books WHERE Section = '{section}' AND IsActive = 1 AND IsBestBook = 1"
    myCursor.execute(sqlQuery)
    bestBooks = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM authors WHERE Section = '{section}' AND IsActive = 1"
    myCursor.execute(sqlQuery)
    authors = myCursor.fetchall()

    myCursor.close()
    return render_template('bookSection.html', bestBooks = bestBooks, authors = authors, section = section)

@app.route("/authorBooks/<name>")
def authorBooks(name):
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM books WHERE Author = '{name}' AND IsActive = 1"
    myCursor.execute(sqlQuery)
    books = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM authors WHERE Name = '{name}'"
    myCursor.execute(sqlQuery)
    author = myCursor.fetchall()
    for authorInfo in author:
        authorDescription = authorInfo[5]
        authorImage = authorInfo[6]
        authorDate = authorInfo[7]

    myCursor.close()
    return render_template('authorBooks.html', books = books, authorDescription = authorDescription, authorImage = authorImage, authorDate = authorDate)

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
        sqlQuery = f"SELECT * FROM users WHERE UserName = '{name}' AND UserPassword = '{password}'"
        myCursor.execute(sqlQuery)
        user = myCursor.fetchall()
        myCursor.close()

        if not user:
            wrongCredentials = True
            return redirect(url_for('adminLogin', wrongCredentials = wrongCredentials))

    return redirect(url_for('adminPage'))

@app.route("/adminContent/<type>")
def adminContent(type):
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM books WHERE Section = '{type}' AND IsActive = 1 AND IsBestBook = 1"
    myCursor.execute(sqlQuery)
    bestBooks = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM authors WHERE Section = '{type}' AND IsActive = 1"
    myCursor.execute(sqlQuery)
    authors = myCursor.fetchall()

    myCursor.close()
    return render_template('adminContent.html', type = type)

if __name__ == "__main__":
    app.run(port=5500, debug=True)