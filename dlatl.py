from flask_apscheduler import APScheduler
from scheduler import schedule_inactive_user_notification

def start_scheduler(app):

    scheduler = APScheduler()
    
    # 먼저 앱과 스케줄러를 연결합니다.
    scheduler.init_app(app)

    # app_context 안에서 작업을 추가해야 app.config 등에 접근할 수 있습니다.
    with app.app_context():
        scheduler.add_job(
            id='inactive_user_notification_task', 
            func=schedule_inactive_user_notification, 
            args=[app], # 작업 함수에 app 객체를 인자로 전달
            trigger='cron', 
            hour=9, 
            minute=0
        )

    # 스케줄러를 시작합니다.
    scheduler.start()
    
    print("✅ 스케줄러가 성공적으로 초기화되고 시작되었습니다.")
