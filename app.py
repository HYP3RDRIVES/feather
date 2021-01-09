from flask import Flask, render_template, send_from_directory, redirect, session, request, escape
from flask_sqlalchemy import SQLAlchemy 
from flask import request   
import os
import datetime
import secrets
from jinja2 import Environment
from os import path
from jinja2.loaders import FileSystemLoader
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['FLASK_HOST'] = os.environ.get('FLASK_HOST')


db = SQLAlchemy(app)


class UserDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50))
    PasswordHash = db.Column(db.String(100))

class StoredData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    linkedUsername = db.Column(db.String(50))
    sharedUrlState = db.Column(db.Boolean)
    sharedUrl = db.Column(db.String(100))
    DateCreated = db.Column(db.DateTime)

if path.exists("db.sqlite") == True:
    print("Database exists")
else:
    print("Creating database")
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def loginPage():
    if session['logged_in'] == True:
        if session['loginerr'] is None:
            loginerr = False
        else:
            loginerr = session['loginerr']
        return render_template("login.html", loginerr=loginerr)

@app.route("/auth", methods=['POST'])
def login():
    username = request.form['USERNAME']
    password = request.form['PASSWORD']
    user = UserDB.query.filter_by(Username=username).First()
    if user is None:
        session['loginerr'] = True
        return("<script>location.replace('/login')</script>")
    elif if user.PasswordHash == hash(password):
        session['loginerr'] = False
        session['logged_in'] = True
        session['Username'] = username
        return("<script>location.replace('/userarea')</script>")

@app.route("/userarea")
def userDash():
    if session['logged_in'] == True:
        username = session['Username']
        instances = StoredData.query.filter_by(linkedUsername=username).order_by(StoredData.date_posted.desc()).all()
        return render_template("userdash.html", instances=instances, username=username)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['Username'] = None

@app.route("/signup/processor", methods=['POST'])
def signupProcessor():
    dest = request.form['USERNAME']
    chars_to_remove = "!\"#$%&'()*+,;/<= >?@[\\]^_`{|}~\t\n\r " # \t TAB, \r: RETURN, \n NEWLINE
    translation_table = {ord(c): None for c in chars_to_remove }
    destsan = dest.translate(translation_table)
    if(destsan != dest):
      injectionerror = 1
    dest = request.form['PASSWORD']
    chars_to_remove = "!\"#$%&'()*+,;/<= >?@[\\]^_`{|}~\t\n\r " # \t TAB, \r: RETURN, \n NEWLINE
    translation_table = {ord(c): None for c in chars_to_remove }
    destsan = dest.translate(translation_table)
    if(destsan != dest):
      injectionerror = 2
    else:
        injectionerror = False
    session['injectionerror'] = injectionerror
    if injectionerror:    
        return("<script>location.replace('/signup')</script>")
    else:
        return("<script>location.replace('/userarea')</script>")


@app.context_processor
def inject_now():
    if not session.get('loginerr'):
        session['loginerr'] = False
