import os
import json
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from pywebpush import webpush, WebPushException
import db_adapter
from flask_jwt_extended import jwt_required, get_jwt_identity

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
    db_adapter.save_subscription(get_jwt_identity(), subscription_data)
    return jsonify({'message': '구독이 성공적으로 완료되었습니다.'}), 201

@push_bp.route('/api/push/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribe():
    db_adapter.delete_subscription(get_jwt_identity())
    return jsonify({'message': '구독이 성공적으로 해지되었습니다.'}), 200

@push_bp.route('/api/push/send-inactive', methods=['POST'])
@require_api_key
def send_to_inactive_users():
    data = request.get_json()
    days_inactive = data.get('days', 7)
    title = data.get('title', '오랫동안 기다렸어요!')
    body = data.get('body', '다시 방문해서 새로운 소식을 확인해보세요!')
    
    inactive_users = db_adapter.get_inactive_users(days_inactive)
    if not inactive_users:
        return jsonify({'message': f'{days_inactive}일 이상 미접속한 구독자가 없습니다.'}), 200

    print(f'총 {len(inactive_users)}명의 휴면 사용자에게 알림을 보냅니다.')
    
    payload = {'title': title, 'body': body}
    success_count, failure_count = 0, 0
    vapid_claims = {"sub": get_config('VAPID_EMAIL')}
    vapid_private_key = get_config('VAPID_PRIVATE_KEY')

    for user in inactive_users:
        sub_info = json.loads(user.push_subscription_json)
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
                print(f'사용자 ID {user.id}의 만료된 구독 정보 삭제')
                db_adapter.delete_subscription(user.id)
            else:
                print(f"알림 전송 실패 (사용자 ID: {user.id}): {ex}")

    return jsonify({
        'message': '알림 전송이 완료되었습니다.',
        'total': len(inactive_users),
        'success': success_count,
        'failure': failure_count
    }), 200
