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

if __name__ == "__main__":
    app.run(port=5500, debug=True)