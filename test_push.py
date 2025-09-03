#!/usr/bin/env python3
"""
푸시 알림 기능 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"
ADMIN_SECRET = "kkkjungle5"

def test_server_health():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 서버 상태: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return False

def test_vapid_key():
    """VAPID 공개키 조회 테스트"""
    try:
        response = requests.get(f"{BASE_URL}/api/push/vapid-key")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VAPID 공개키 조회 성공: {data.get('publicKey', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ VAPID 공개키 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VAPID 공개키 조회 오류: {e}")
        return False

def test_admin_push():
    """관리자 알림 발송 테스트"""
    try:
        headers = {
            "Authorization": f"Bearer {ADMIN_SECRET}",
            "Content-Type": "application/json"
        }
        data = {
            "days": 0,
            "title": "테스트 알림",
            "body": "로컬 테스트 성공!"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/push/send-inactive",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 관리자 알림 발송 성공: {result}")
            return True
        else:
            print(f"❌ 관리자 알림 발송 실패: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 관리자 알림 발송 오류: {e}")
        return False

def main():
    print("🚀 푸시 알림 기능 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    if not test_server_health():
        return
    
    # 2. VAPID 키 확인
    if not test_vapid_key():
        print("⚠️  VAPID 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    # 3. 관리자 알림 발송 테스트
    test_admin_push()
    
    print("\n📋 브라우저 테스트 가이드:")
    print("1. 브라우저에서 http://localhost:5001 접속")
    print("2. 회원가입 후 로그인")
    print("3. 메인 페이지에서 푸시 알림 허용")
    print("4. 개발자 도구 콘솔에서 구독 상태 확인")

if __name__ == "__main__":
    main()
