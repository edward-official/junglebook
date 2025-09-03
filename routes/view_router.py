from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager, set_access_cookies, unset_jwt_cookies
from flask import Blueprint, render_template

render_blueprint = Blueprint("main", __name__, url_prefix="/")


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
def profile():
    return render_template("list.html")
