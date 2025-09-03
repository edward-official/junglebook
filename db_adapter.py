import os
import json
from datetime import datetime, timedelta
from flask import current_app

# --- 임시(Mock) DB 설정 ---
MOCK_DB_FILE = 'mock_user_subscriptions.json'
MOCK_USERS_FILE = 'mock_users.json'

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

def _load_mock_users():
    if not os.path.exists(MOCK_USERS_FILE):
        return {}
    try:
        with open(MOCK_USERS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def _save_mock_users(users):
    with open(MOCK_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# ============================
# 1. 사용자 관리 함수들
# ============================
def create_user(userid, username, password):
    """사용자 생성"""
    try:
        db_mode = current_app.config.get('DB_MODE', 'mock')
        
        if db_mode == 'real':
            return _create_user_real(userid, username, password)
        else:
            return _create_user_mock(userid, username, password)
    except Exception as e:
        print(f"사용자 생성 오류: {e}")
        return {'success': False, 'message': '사용자 생성 중 오류가 발생했습니다.'}

def authenticate_user(userid, password):
    """사용자 인증"""
    try:
        db_mode = current_app.config.get('DB_MODE', 'mock')
        
        if db_mode == 'real':
            return _authenticate_user_real(userid, password)
        else:
            return _authenticate_user_mock(userid, password)
    except Exception as e:
        print(f"사용자 인증 오류: {e}")
        return {'success': False, 'message': '사용자 인증 중 오류가 발생했습니다.'}

def _create_user_mock(userid, username, password):
    """Mock DB에 사용자 생성"""
    users = _load_mock_users()
    
    if userid in users:
        return {'success': False, 'message': '이미 사용 중인 아이디입니다.'}
    
    bcrypt = current_app.config['BCRYPT']
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    
    users[userid] = {
        "username": username,
        "userid": userid,
        "password": hashed,
        "created_at": datetime.utcnow().isoformat()
    }
    
    _save_mock_users(users)
    print(f"📝 Mock DB 사용자 생성: {userid}")
    return {'success': True, 'message': '회원가입이 완료되었습니다.'}

def _authenticate_user_mock(userid, password):
    """Mock DB에서 사용자 인증"""
    users = _load_mock_users()
    
    if userid not in users:
        return {'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}
    
    user = users[userid]
    bcrypt = current_app.config['BCRYPT']
    
    if not bcrypt.check_password_hash(user['password'], password):
        return {'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}
    
    print(f"📝 Mock DB 사용자 로그인: {userid}")
    return {'success': True, 'message': '로그인 성공'}

def _create_user_real(userid, username, password):
    """실제 DB에 사용자 생성"""
    try:
        database = current_app.config['DB']
        users = database.users
        
        if users.find_one({"userid": userid}):
            return {'success': False, 'message': '이미 사용 중인 아이디입니다.'}
        
        bcrypt = current_app.config['BCRYPT']
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        
        users.insert_one({
            "username": username,
            "userid": userid,
            "password": hashed,
            "created_at": datetime.utcnow()
        })
        
        print(f"📝 Real DB 사용자 생성: {userid}")
        return {'success': True, 'message': '회원가입이 완료되었습니다.'}
    except Exception as e:
        print(f"실제 DB 사용자 생성 오류: {e}")
        return {'success': False, 'message': '데이터베이스 오류가 발생했습니다.'}

def _authenticate_user_real(userid, password):
    """실제 DB에서 사용자 인증"""
    try:
        database = current_app.config['DB']
        users = database.users
        
        user = users.find_one({"userid": userid})
        if not user:
            return {'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}
        
        bcrypt = current_app.config['BCRYPT']
        if not bcrypt.check_password_hash(user['password'], password):
            return {'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}
        
        print(f"📝 Real DB 사용자 로그인: {userid}")
        return {'success': True, 'message': '로그인 성공'}
    except Exception as e:
        print(f"실제 DB 사용자 인증 오류: {e}")
        return {'success': False, 'message': '데이터베이스 오류가 발생했습니다.'}

# ============================
# 2. 푸시 알림 관련 함수들 (기존)
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
