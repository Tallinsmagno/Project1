import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    session["isloggedin"] = None
    return render_template("index.html", isloggedin=session["isloggedin"])

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logedin", methods=["POST"])
def logedin():
    error = None

    session["name"] = request.form.get("name")
    session["password"] = request.form.get("password")
    session["user"] = db.execute("SELECT * FROM users WHERE (name = :name) AND (password = :password)", {"name": session["name"],"password": session["password"]}).fetchone()
    if session["user"] == None:
        error = "Incorrect username or password. Please try again"
        return render_template("login.html", error=error)
    session["isloggedin"] = True
    return render_template("logedin.html", name=session["name"], isloggedin=session["isloggedin"])

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signedup", methods=["POST"])
def signedup():
    error = None

    name = request.form.get("name")
    password = request.form.get("password")
    isnamein = db.execute("SELECT * FROM users WHERE name= :name", {"name": name}).rowcount

    if isnamein > 0:
        error = "The username you chose already exists, please pick a different one."
        return render_template("signup.html", error=error)

    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",
                  {"name": name, "password": password})
    db.commit()
    return render_template("signedup.html", name=name)
