#!/usr/bin/env python3
"""
푸시 알림 발송 테스트 스크립트
"""

import requests
import json

def send_push_notification():
    """푸시 알림 발송"""
    url = "http://localhost:5001/api/push/send-inactive"
    headers = {
        "Authorization": "Bearer kkkjungle5",
        "Content-Type": "application/json"
    }
    data = {
        "days": 0,
        "title": "테스트 알림",
        "body": "푸시 알림이 성공적으로 동작합니다!"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"응답 상태: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 푸시 알림 발송 테스트")
    print("=" * 30)
    
    success = send_push_notification()
    
    if success:
        print("✅ 알림 발송 성공!")
    else:
        print("❌ 알림 발송 실패")
