from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import db_adapter
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    userid = request.form.get('userid')
    password = request.form.get('password')
    if not userid or not password:
        return jsonify({"result": "fail", "code": "E0", "msg": "userid/password required"})

    # DB 어댑터를 통해 사용자 생성
    try:
        result = db_adapter.create_user(userid, username, password)
        if result['success']:
            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "fail", "code": "E1", "msg": result['message']})
    except Exception as e:
        print(f"회원가입 오류: {e}")
        return jsonify({"result": "fail", "msg": "회원가입 중 오류가 발생했습니다."})

@auth_bp.route('/login', methods=['POST'])
def login():
    userid = request.form.get('userid')
    password = request.form.get('password')
    if not userid or not password:
        return jsonify({"result": "fail", "msg": "userid/password required"})
    
    # DB 어댑터를 통해 사용자 인증
    try:
        result = db_adapter.authenticate_user(userid, password)
        if result['success']:
            access_token = create_access_token(identity=userid)
            return jsonify({"result": "success", "access_token": access_token})
        else:
            return jsonify({"result": "fail", "msg": result['message']})
    except Exception as e:
        print(f"로그인 오류: {e}")
        return jsonify({"result": "fail", "msg": "로그인 중 오류가 발생했습니다."})

@auth_bp.route('/example', methods=['GET'])
@jwt_required()
def example():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {current_user}! This is a example route."})