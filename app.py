import os
from flask import Flask, redirect, url_for
from flask.json.provider import JSONProvider
from bson import ObjectId
import json
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from routes.view_router import render_blueprint
from routes.tils import tils_bp
from routes.auth import auth_bp
from routes.push_notifications import push_bp
from dlatl import start_scheduler
from dotenv import load_dotenv
import os

class Config:
    SCHEDULER_API_ENABLED = True
app = Flask(__name__)
mongoDB = MongoClient('localhost', 27017)
database = mongoDB.jungle_book
bcrypt = Bcrypt(app)
load_dotenv()

app.config['DB'] = database
app.config['BCRYPT'] = bcrypt
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Strict"
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
jwt = JWTManager(app)

app.config['ADMIN_SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'your-admin-secret')
app.config['VAPID_PUBLIC_KEY'] = os.getenv('VAPID_PUBLIC_KEY', 'your-vapid-public-key')
app.config['VAPID_PRIVATE_KEY'] = os.getenv('VAPID_PRIVATE_KEY', 'your-vapid-private-key')
app.config['VAPID_EMAIL'] = os.getenv('VAPID_EMAIL', 'your-email@example.com')

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)
    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)
app.register_blueprint(tils_bp)
app.register_blueprint(render_blueprint)
app.register_blueprint(auth_bp)
app.register_blueprint(push_bp)
start_scheduler(app)

def _redirect_to_login():
  resp = redirect(url_for("main.login"))
  unset_jwt_cookies(resp)
  return resp

@jwt.unauthorized_loader
def handle_missing_token(reason):
  return _redirect_to_login()

@jwt.invalid_token_loader
def handle_invalid_token(reason):
  return _redirect_to_login()

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
  return _redirect_to_login()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
