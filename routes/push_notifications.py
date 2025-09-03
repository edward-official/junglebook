from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from pywebpush import webpush, WebPushException
from flask_jwt_extended import jwt_required, get_jwt_identity
import json, datetime

push_bp = Blueprint('push', __name__)

def get_config(key):
    return current_app.config.get(key)


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


def send_web_push(users_to_notify, payload):
    """
    주어진 사용자 목록에게 웹 푸시 알림을 전송합니다.
    
    :param users_to_notify: 알림을 받을 사용자 객체의 리스트 (DB에서 조회한 결과)
    :param payload: 알림에 담길 데이터 (dict 형태, e.g., {'title': '...', 'body': '...'})
    """
    database = get_config('DB')
    users = database.users
    vapid_claims = {"sub": get_config('VAPID_EMAIL')}
    vapid_private_key = get_config('VAPID_PRIVATE_KEY')
    
    success_count, failure_count = 0, 0

    for user in users_to_notify:
        try:
            sub_info = json.loads(user['push_subscription_json'])
            webpush(
                subscription_info=sub_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims.copy()
            )
            success_count += 1
        except WebPushException as ex:
            failure_count += 1
            # 구독이 만료되었거나(Not Found, Gone) 잘못된 경우 DB에서 구독 정보 삭제
            if ex.response and ex.response.status_code in [404, 410]:
                print(f"만료된 구독 정보 삭제 (사용자 ID: {user['userid']})")
                users.update_one({"userid": user['userid']}, {"$unset": {"push_subscription_json": ""}})
            else:
                print(f"알림 전송 실패 (사용자 ID: {user['userid']}): {ex}")
        except Exception as e:
            # json.loads 실패 등 기타 예외 처리
            failure_count += 1
            print(f"알림 처리 중 오류 발생 (사용자 ID: {user['userid']}): {e}")

    print(f"알림 전송 결과: 총 {len(users_to_notify)}명 중 성공 {success_count}명, 실패 {failure_count}명")
    return success_count, failure_count