from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from pywebpush import webpush, WebPushException
from flask_jwt_extended import jwt_required, get_jwt_identity
import json, datetime

push_bp = Blueprint('push', __name__)

def get_config(key):
    return current_app.config.get(key)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        admin_secret_key = get_config('ADMIN_SECRET_KEY')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header is missing or invalid"}), 401
        token = auth_header.split(' ')[1]
        if token != admin_secret_key:
            return jsonify({"error": "Invalid secret key"}), 403
        return f(*args, **kwargs)
    return decorated_function

@push_bp.route('/service-worker.js')
def service_worker():
    return current_app.send_static_file('script/service-worker.js')

@push_bp.route('/api/push/vapid-key', methods=['GET'])
def get_vapid_public_key():
    return jsonify({'publicKey': get_config('VAPID_PUBLIC_KEY')})

@push_bp.route('/api/push/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    subscription_data = request.get_json()
    if not subscription_data or 'endpoint' not in subscription_data:
        return jsonify({'error': 'Invalid subscription data'}), 400
    database = current_app.config['DB']
    users = database.users
    user_id = get_jwt_identity()
    
    users.update_one(
        {"userid": user_id},
        {"$set": {"push_subscription_json": json.dumps(subscription_data)}}
    )
    return jsonify({'message': '구독이 성공적으로 완료되었습니다.'}), 201

@push_bp.route('/api/push/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribe():
    database = current_app.config['DB']
    users = database.users
    user_id = get_jwt_identity()
    
    users.update_one(
        {"userid": user_id},
        {"$unset": {"push_subscription_json": ""}}
    )
    return jsonify({'message': '구독이 성공적으로 해지되었습니다.'}), 200



@push_bp.route('/api/push/send-inactive', methods=['POST'])
@require_api_key
def send_to_inactive_users():
    database = current_app.config['DB']
    users = database.users

    data = request.get_json()
    days_inactive = data.get('days', 7)
    title = data.get('title', '오랫동안 기다렸어요!')
    body = data.get('body', '다시 방문해서 새로운 소식을 확인해보세요!')

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days_inactive)
    inactive_users = list(users.find({
        "last_login": {"$lte": cutoff},
        "push_subscription_json": {"$exists": True}
    }))

    if not inactive_users:
        return jsonify({'message': f'{days_inactive}일 이상 미접속한 구독자가 없습니다.'}), 200

    payload = {'title': title, 'body': body}
    success_count, failure_count = 0, 0
    vapid_claims = {"sub": get_config('VAPID_EMAIL')}
    vapid_private_key = get_config('VAPID_PRIVATE_KEY')

    for user in inactive_users:
        sub_info = json.loads(user['push_subscription_json'])
        try:
            webpush(
                subscription_info=sub_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims.copy()
            )
            success_count += 1
        except WebPushException as ex:
            failure_count += 1
            if ex.response and ex.response.status_code in [404, 410]:
                users.update_one({"userid": user['userid']}, {"$unset": {"push_subscription_json": ""}})
            else:
                print(f"알림 전송 실패 (사용자 ID: {user['userid']}): {ex}")

    return jsonify({
        'message': '알림 전송이 완료되었습니다.',
        'total': len(inactive_users),
        'success': success_count,
        'failure': failure_count
    }), 200


@push_bp.route('/api/push/send-all', methods=['POST'])
@require_api_key
def send_to_all_users():
    database = current_app.config['DB']
    users = database.users

    # 요청에서 알림 제목/내용 받기
    data = request.get_json()
    title = data.get('title', '전체 알림')
    body = data.get('body', '모든 사용자에게 보내는 테스트 알림입니다.')

    # push_subscription_json이 있는 모든 사용자 가져오기
    subscribed_users = list(users.find({"push_subscription_json": {"$exists": True}}))

    if not subscribed_users:
        return jsonify({'message': '푸시 구독한 사용자가 없습니다.'}), 200

    payload = {'title': title, 'body': body}
    success_count, failure_count = 0, 0
    vapid_claims = {"sub": get_config('VAPID_EMAIL')}
    vapid_private_key = get_config('VAPID_PRIVATE_KEY')

    for user in subscribed_users:
        sub_info = json.loads(user['push_subscription_json'])
        try:
            webpush(
                subscription_info=sub_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims.copy()
            )
            success_count += 1
        except WebPushException as ex:
            failure_count += 1
            # 구독 만료된 경우 삭제
            if ex.response and ex.response.status_code in [404, 410]:
                users.update_one({"userid": user['userid']}, {"$unset": {"push_subscription_json": ""}})
            else:
                print(f"알림 전송 실패 (사용자 ID: {user['userid']}): {ex}")

    return jsonify({
        'message': '전체 알림 전송이 완료되었습니다.',
        'total': len(subscribed_users),
        'success': success_count,
        'failure': failure_count
    }), 200