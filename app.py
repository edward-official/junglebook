import os
from flask import Flask
from flask.json.provider import JSONProvider
from bson import ObjectId
import json
from routes.view_router import render_blueprint
from flask_bcrypt import Bcrypt
from routes.auth import auth_bp
from flask_jwt_extended import JWTManager
from routes.push_notifications import push_bp
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# MongoDB 연결 (선택적)
DB_MODE = "mock"  # 기본값을 mock으로 설정
database = None

try:
    from pymongo import MongoClient
    mongoDB = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)  # 2초 타임아웃
    # 연결 테스트
    mongoDB.admin.command('ping')
    database = mongoDB.jungle_book
    DB_MODE = "real"
    print("✅ MongoDB 연결 성공")
except Exception as e:
    print(f"⚠️  MongoDB 연결 실패: {e}")
    print("📝 Mock DB 모드를 사용합니다.")
    database = None
    DB_MODE = "mock"

bcrypt = Bcrypt(app)

app.config['DB'] = database
app.config['DB_MODE'] = DB_MODE
app.config['BCRYPT'] = bcrypt
app.config['JWT_SECRET_KEY'] = "super-secret-key"
jwt = JWTManager(app)

# 환경변수 기반 푸시/관리자 키 설정 (기본값 포함)
app.config['ADMIN_SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'test-admin-secret-key-123')
app.config['VAPID_PUBLIC_KEY'] = os.getenv('VAPID_PUBLIC_KEY', 'BLBz8vO2tXg4AjdkqEdT8EfbN5eNYwZAPY6J_XdHXlE')
app.config['VAPID_PRIVATE_KEY'] = os.getenv('VAPID_PRIVATE_KEY', 'dGVzdC1wcml2YXRlLWtleS1mb3ItbG9jYWwtdGVzdGluZw==')
app.config['VAPID_EMAIL'] = os.getenv('VAPID_EMAIL', 'test@example.com')

print("✅ 푸시 알림 설정 완료")
print(f"   - DB_MODE: {DB_MODE}")
print(f"   - ADMIN_SECRET_KEY: {app.config['ADMIN_SECRET_KEY'][:10]}...")
print(f"   - VAPID_PUBLIC_KEY: {app.config['VAPID_PUBLIC_KEY'][:10]}...")
print(f"   - VAPID_EMAIL: {app.config['VAPID_EMAIL']}")


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
