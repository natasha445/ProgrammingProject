from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mysqldb import MySQL
import os
import shutil
import requests

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bookstore'

mysql = MySQL(app)

app.secret_key = "myKey"
api_key = "fa3f1a75c3e633cf866dbab5b028542f5fbd9"

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
        
        bookDuplicate = checkBookDuplicate(bookTitle)
        authorExists = checkIfAuthorExists(bookAuthor)

        if bookDuplicate == 1:
            flash('Book already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertBooks'))
        else:
            if authorExists == 0:
                flash('The author does not exists or is inactive, the book was not added')
                return redirect(url_for('adminContent', type = 'insertBooks'))
            else:
                myCursor = mysql.connection.cursor()
                validatedAuthorSection = validateAuthorSection(bookAuthor, bookSection)

                if validatedAuthorSection == 0:
                    flash('The book section does not coincide with the author section, the book was not added')
                    return redirect(url_for('adminContent', type = 'insertBooks'))

                apiUrl = f"https://cutt.ly/api/api.php?key={api_key}&short={bookDownloadUrl}"
                data = requests.get(apiUrl).json()["url"]
                shortenedUrl = data["shortLink"]

                myCursor.execute("INSERT INTO books (Title, Author, Year, DownloadUrl, BookTooltip, BookSection, IsActive, Type, BookImage, IsBestBook, IsClassicBook)" +
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (bookTitle, bookAuthor, bookYear, shortenedUrl, bookDescription, bookSection, 1, bookType, 
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

        userDuplicate = checkUserDuplicate(userName)

        if userDuplicate == 1:
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
        authorImageSrc = '/static/authors' + authorImage[-1]
        
        authorDuplicate = checkAuthorDuplicate(authorName)

        if authorDuplicate == 1:
            flash('Author already exists on Data Base')
            return redirect(url_for('adminContent', type = 'insertAuthors'))
        else:
            if authorSection != "Philosophy" and authorSection != "Science Fiction" and authorSection != "Novels":
                flash('The author section must be philosophy, novels or science fiction')
                return redirect(url_for('adminContent', type = 'insertAuthors'))

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
            flash('Book does not exists or is not active')
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
            flash('User does not exists or is not active')
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
            flash('Author does not exists or is not active')
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

        myCursor = mysql.connection.cursor()
        sqlQuery = f"SELECT * FROM usersUpdateView WHERE UserName = '{userName}'" #muestra los campos especificos
        myCursor.execute(sqlQuery)
        userInfo = myCursor.fetchall()
        myCursor.close()

        if not userInfo:
            flash("User does not exists on Data Base, it cannot be updated")
            return redirect(url_for('adminContent', type = 'updateUsers'))

    return render_template('updateUserInfo.html', userInfo = userInfo, userName = userName)

@app.route("/sendUpdatedUserInfo/<user>", methods=['POST'])
def sendUpdatedUserInfo(user):
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

@app.route("/updateBook/", methods=['POST'])
def updateBook():
    if request.method == "POST":
        bookTitle = request.form['bookTitle']

        myCursor = mysql.connection.cursor()
        sqlQuery = f"SELECT * FROM booksUpdateView WHERE Title = '{bookTitle}'"
        myCursor.execute(sqlQuery)
        bookInfo = myCursor.fetchall()
        myCursor.close()

        if not bookInfo:
            flash("Book does not exists on Data Base, it cannot be updated")
            return redirect(url_for('adminContent', type = 'updateBooks'))

    return render_template('updateBookInfo.html', bookInfo = bookInfo, bookTitle = bookTitle)

@app.route("/sendUpdatedBookInfo/<title>", methods=['POST'])
def sendUpdatedBookInfo(title):
    if request.method == "POST":
        bookTitle = request.form['bookTitle']
        bookAuthor = request.form['bookAuthor']
        bookYear = request.form['bookYear']
        bookType = request.form['bookType']
        bookSection = request.form['bookSection']
        activeBook = int(request.form['activeBook'])
        bestBook = int(request.form['bestBook'])
        classicBook = int(request.form['classicBook'])
        bookDownloadUrl = request.form['bookDownloadUrl']
        bookOldImageSrc = request.form['bookOldImageSrc']
        bookNewImageSrc = request.form['bookNewImageSrc']
        bookDescription = request.form['bookDescription']

        if not bookNewImageSrc:
            bookUpdatedImage = bookOldImageSrc
        else:
            bookSplitedImage = bookOldImageSrc.split(os.sep)
            bookImage = '/static/images/authors/' + bookSplitedImage[-1]
            bookUpdatedImage = bookImage
            moveAuthorImageToFolder(bookSplitedImage[-1])

        myCursor = mysql.connection.cursor()
        myCursor.execute("UPDATE books SET Title = %s, Author = %s, Year = %s, Type = %s, BookSection = %s, IsActive = %s, " + 
        "IsBestBook = %s, IsClassicBook = %s, DownloadUrl = %s, BookImage = %s, BookTooltip = %s WHERE Title = %s", 
        (bookTitle, bookAuthor, bookYear, bookType, bookSection, activeBook, bestBook, classicBook, bookDownloadUrl,
        bookUpdatedImage, bookDescription, title))
        mysql.connection.commit()
        myCursor.close()
        
    return redirect(url_for('adminPage'))

@app.route("/updateAuthor/", methods=['POST'])
def updateAuthor():
    if request.method == "POST":
        authorName = request.form['authorName']

        myCursor = mysql.connection.cursor()
        sqlQuery = f"SELECT * FROM authorUpdateView WHERE Name = '{authorName}'"
        myCursor.execute(sqlQuery)
        authorInfo = myCursor.fetchall()
        myCursor.close()

        if not authorInfo:
            flash("Author does not exists on Data Base, it cannot be updated")
            return redirect(url_for('adminContent', type = 'updateAuthors'))

    return render_template('updateAuthorInfo.html', authorInfo = authorInfo, authorName = authorName)

@app.route("/sendUpdatedAuthorInfo/<author>", methods=['POST'])
def sendUpdatedAuthorInfo(author):
    if request.method == "POST":
        #authorSplitedImage = ""

        authorName = request.form['authorName']
        authorSection = request.form['authorSection']
        birthDeathDate = request.form['birthDeathDate']
        authorActive = int(request.form['authorActive'])
        authorDescription = request.form['authorDescription']
        authorNewImageSrc = request.form['authorNewImageSrc']
        authorOldImageSrc = request.form['authorOldImageSrc']

        if not authorNewImageSrc:
            authorUpdatedImage = authorOldImageSrc
        else:
            authorSplitedImage = authorNewImageSrc.split(os.sep)
            authorImage = '/static/images/authors/' + authorSplitedImage[-1]
            authorUpdatedImage = authorImage
            moveAuthorImageToFolder(authorSplitedImage[-1])

        myCursor = mysql.connection.cursor()
        myCursor.execute("UPDATE authors SET Name = %s, Section = %s, BirthDeathDate = %s, " + 
        "IsActive = %s, Description = %s, AuthorImage = %s WHERE Name = %s", 
        (authorName, authorSection, birthDeathDate, authorActive, authorDescription, authorUpdatedImage, author))
        mysql.connection.commit()
        myCursor.close()

    return redirect(url_for('adminPage'))

@app.route("/adminContent/<type>")
def adminContent(type):
    myCursor = mysql.connection.cursor()
    sqlQuery = f"SELECT * FROM usersView"
    myCursor.execute(sqlQuery)
    userTableInfo = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM booksView"
    myCursor.execute(sqlQuery)
    booksTableInfo = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM authorsView"
    myCursor.execute(sqlQuery)
    authorsTableInfo = myCursor.fetchall()

    sqlQuery = f"SELECT * FROM requestsView"
    myCursor.execute(sqlQuery)
    requestTableInfo = myCursor.fetchall()
    myCursor.close()

    return render_template('adminContent.html', type = type, usersTableInfo = userTableInfo, requestTableInfo = requestTableInfo,
    booksTableInfo = booksTableInfo, authorsTableInfo = authorsTableInfo)

def checkIfBookExists(bookTitle):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT BookExists (%s)", (bookTitle,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        bookExists = result[0]

    myCursor.close()
    return bookExists

def checkBookDuplicate(bookTitle):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT BookDuplicate (%s)", (bookTitle,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        bookDuplicate = result[0]

    myCursor.close()
    return bookDuplicate

def checkAuthorDuplicate(authorName):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT AuthorDuplicate (%s)", (authorName,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        authorDuplicate = result[0]

    myCursor.close()
    return authorDuplicate

def checkUserDuplicate(userName):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT UserDuplicate (%s)", (userName,))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        userDuplicate = result[0]

    myCursor.close()
    return userDuplicate

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

def validateAuthorSection(authorName, section):
    myCursor = mysql.connection.cursor()
    myCursor.execute("SELECT AuthorSectionValidation (%s, %s)", (authorName, section))
    functionResult = myCursor.fetchall()

    for result in functionResult:
        validatedAuthorSection = result[0]

    myCursor.close()
    return validatedAuthorSection

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