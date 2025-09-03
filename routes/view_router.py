from flask import Blueprint, render_template, redirect, url_for

render_blueprint = Blueprint("main", __name__, url_prefix="/")


@render_blueprint.route("/")
def index():
    return redirect(url_for("main.login"))

@render_blueprint.route("/login")
def login():
    return render_template("login.html")

@render_blueprint.route("/signup")
def signup():
    return render_template("signup.html")

@render_blueprint.route("/main")
def dashboard():
    return render_template("main.html")

@render_blueprint.route("/list")
def profile():
    return render_template("list.html")
