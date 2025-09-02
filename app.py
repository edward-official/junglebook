import os
from flask import Flask
from flask.json.provider import JSONProvider
from bson import ObjectId
import json
from routes.view_router import render_blueprint
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from routes.auth import auth_bp
from flask_jwt_extended import JWTManager
from routes.push_notifications import push_bp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
mongoDB = MongoClient('localhost', 27017)
database = mongoDB.jungle_book
bcrypt = Bcrypt(app)

app.config['DB'] = database
app.config['BCRYPT'] = bcrypt
app.config['JWT_SECRET_KEY'] = "super-secret-key"
jwt = JWTManager(app)


# 환경변수 기반 푸시/관리자 키 설정
app.config['ADMIN_SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY')
app.config['VAPID_PUBLIC_KEY'] = os.getenv('VAPID_PUBLIC_KEY')
app.config['VAPID_PRIVATE_KEY'] = os.getenv('VAPID_PRIVATE_KEY')
app.config['VAPID_EMAIL'] = os.getenv('VAPID_EMAIL')

# 선택: 필수값 누락 시 안전 가드
missing = [k for k in ['ADMIN_SECRET_KEY','VAPID_PUBLIC_KEY','VAPID_PRIVATE_KEY','VAPID_EMAIL'] if not app.config.get(k)]
if missing:
    raise RuntimeError(f"Missing required config(s): {', '.join(missing)}")


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
app.register_blueprint(render_blueprint)
app.register_blueprint(auth_bp)


app.register_blueprint(push_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
