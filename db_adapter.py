import os
import json
from datetime import datetime, timedelta

# --- 임시(Mock) DB 설정 ---
MOCK_DB_FILE = 'mock_user_subscriptions.json'

def _load_mock_db():
    if not os.path.exists(MOCK_DB_FILE):
        return {}
    try:
        with open(MOCK_DB_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def _save_mock_db(db):
    with open(MOCK_DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

# ============================
# 1. 임시(Mock) DB 함수들
# ============================
def mock_save_subscription(user_id, subscription_data):
    db = _load_mock_db()
    if 'users' not in db:
        db['users'] = {}
    
    db['users'][str(user_id)] = {
        "push_subscription_json": json.dumps(subscription_data),
        "last_login": datetime.utcnow().isoformat()
    }
    _save_mock_db(db)
    print(f"[MOCK DB] 사용자 {user_id}의 구독 정보 저장 완료.")

def mock_delete_subscription(user_id):
    db = _load_mock_db()
    if 'users' in db and str(user_id) in db['users']:
        db['users'][str(user_id)]["push_subscription_json"] = None
        _save_mock_db(db)
        print(f"[MOCK DB] 사용자 {user_id}의 구독 정보 삭제 완료.")

def mock_get_inactive_users(days_inactive):
    db = _load_mock_db()
    inactive_users = []
    if 'users' not in db:
        return []
        
    inactive_threshold = datetime.utcnow() - timedelta(days=days_inactive)
    
    for user_id, user_data in db['users'].items():
        if user_data.get("push_subscription_json"):
            last_login_iso = user_data.get("last_login")
            if last_login_iso:
                last_login = datetime.fromisoformat(last_login_iso)
                if last_login < inactive_threshold:
                    mock_user = type('MockUser', (object,), {
                        'id': user_id, 
                        'push_subscription_json': user_data['push_subscription_json']
                    })
                    inactive_users.append(mock_user)
    return inactive_users

# ============================
# 2. 실제 DB 함수들 (나중에 완성)
# ============================
def real_save_subscription(user_id, subscription_data):
    from models import User  # 실제 User 모델 임포트
    from app import db  # 실제 db 객체 임포트
    user = User.query.filter_by(userid=user_id).first()
    if not user:
        raise ValueError("User not found")
    user.push_subscription_json = json.dumps(subscription_data)
    db.session.commit()
    print(f"[REAL DB] 사용자 {user_id}의 구독 정보 저장 완료.")

def real_delete_subscription(user_id):
    from models import User
    from app import db
    user = User.query.filter_by(userid=user_id).first()
    if not user:
        return
    user.push_subscription_json = None
    db.session.commit()
    print(f"[REAL DB] 사용자 {user_id}의 구독 정보 삭제 완료.")

def real_get_inactive_users(days_inactive):
    from models import User
    inactive_threshold = datetime.utcnow() - timedelta(days=days_inactive)
    return User.query.filter(
        User.last_login < inactive_threshold,
        User.push_subscription_json.isnot(None)
    ).all()

# ============================
# 3. DB 모드 전환 어댑터 함수
# ============================
DB_MODE = os.getenv("DB_MODE", "mock")

def save_subscription(user_id, subscription_data):
    if DB_MODE == 'real':
        return real_save_subscription(user_id, subscription_data)
    else:
        return mock_save_subscription(user_id, subscription_data)

def delete_subscription(user_id):
    if DB_MODE == 'real':
        return real_delete_subscription(user_id)
    else:
        return mock_delete_subscription(user_id)
        
def get_inactive_users(days_inactive):
    if DB_MODE == 'real':
        return real_get_inactive_users(days_inactive)
    else:
        return mock_get_inactive_users(days_inactive)
