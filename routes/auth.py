from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    userid = request.form.get('userid')
    password = request.form.get('password')
    if not userid or not password:
        return jsonify({"result": "fail", "code": "E0", "msg": "userid/password required"})

    database = current_app.config['DB']
    users = database.users
    if users.find_one({"userid": userid}):
        return jsonify({"result": "fail", "code": "E1", "msg": "userid already exists"})
    
    bcrypt = current_app.config['BCRYPT']
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    users.insert_one({
        "username": username,
        "userid": userid,
        "password": hashed
    })
    return jsonify({"result": "success"})

@auth_bp.route('/login', methods=['POST'])
def login():
    userid = request.form.get('userid')
    password = request.form.get('password')
    if not userid or not password:
        return jsonify({"result": "fail", "msg": "userid/password required"})
    
    database = current_app.config['DB']
    users = database.users
    user = users.find_one({"userid": userid})
    if not user:
        return jsonify({"result": "fail", "msg": "invalid credentials"})
    
    bcrypt = current_app.config['BCRYPT']
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"result": "fail", "msg": "invalid credentials"})
    
    access_token = create_access_token(identity=userid)
    return jsonify({"result": "success", "access_token": access_token})

@auth_bp.route('/example', methods=['GET'])
@jwt_required()
def example():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {current_user}! This is a example route."})