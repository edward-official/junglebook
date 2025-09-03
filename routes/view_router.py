from datetime import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, render_template, redirect, url_for, request, current_app

render_blueprint = Blueprint("main", __name__, url_prefix="/")

@render_blueprint.route("/")
@jwt_required(optional=True)
def index():
    current_user = get_jwt_identity()
    if current_user:
        return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("main.login"))

@render_blueprint.route("/login")
def login():
    return render_template("login.html")

@render_blueprint.route("/signup")
def signup():
    return render_template("signup.html")

@render_blueprint.route("/main")
@jwt_required()
def dashboard():
    return render_template("main.html")

@render_blueprint.route("/list")
@jwt_required()
def list():
    current_user = get_jwt_identity()
    database = current_app.config['DB']
    date = request.args.get("date")
    today = datetime.now().strftime("%Y-%m-%d")
    if not date or not is_valid_date(date):
        return redirect(url_for("main.list", date=today))

    data = database.tils.find_one({"username": current_user, "learnedDate": date})

    return render_template("list.html", url=data["url"] if data else "", isFuture=date > today)

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False