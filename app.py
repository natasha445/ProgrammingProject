from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/philosophyBooks/")
def aboutUs():
    return render_template("philosophyBooks.html")

@app.route("/contact/")
def services():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(port=5500, debug=True)