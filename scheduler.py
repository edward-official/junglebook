import datetime
from routes.push_notifications import send_web_push 

def schedule_inactive_user_notification(app):
    """
    7일 이상 미접속 사용자에게 알림을 보내는 스케줄링된 작업입니다.
    Flask app context 내에서 실행되어야 합니다.
    """
    with app.app_context():
        print(f"[{datetime.datetime.now()}] 미접속 사용자 알림 스케줄러 실행...")
        
        database = app.config['DB']
        users_collection = database.users
        # 7일 이상 미접속 기준 시간
        days_inactive = 7
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days_inactive)
        
        # 대상 사용자 조회: 마지막 로그인이 7일 이전이고, 푸시 구독 정보가 있는 사용자
        inactive_users = list(users_collection.find({
            "last_login": {"$lte": cutoff},
            "push_subscription_json": {"$exists": True}
        }))


        if not inactive_users:
            print(f"결과: {days_inactive}일 이상 미접속한 구독자가 없습니다.")
            return

        print(f"결과: {len(inactive_users)}명의 미접속 사용자에게 알림을 전송합니다.")

        # 알림 내용 정의
        payload = {
            'title': '오랫동안 기다렸어요!',
            'body': '다시 방문해서 새로운 소식을 확인해보세요!'
        }
        
        # 알림 전송 함수 호출
        send_web_push(inactive_users, payload)