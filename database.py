import sqlite3
import json

DB_NAME = 'subscriptions.db'

def get_db_connection():
    """데이터베이스 연결 객체를 생성하고 반환합니다."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 컬럼 이름으로 접근 가능하게 설정
    return conn

def init_db():
    """
    'subscriptions' 테이블이 없으면 새로 생성하여 데이터베이스를 초기화합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("데이터베이스가 성공적으로 초기화되었습니다.")

def add_subscription(subscription_data):
    """
    새로운 구독 정보를 데이터베이스에 추가하거나, endpoint가 이미 존재하면 업데이트합니다.
    - subscription_data: 푸시 서비스에서 받은 JSON 객체
    """
    endpoint = subscription_data.get('endpoint')
    data_str = json.dumps(subscription_data)

    conn = get_db_connection()
    cursor = conn.cursor()
    # ON CONFLICT(endpoint) DO UPDATE SET data=excluded.data;
    # endpoint가 중복되면 data 필드만 업데이트하여 중복 저장을 방지합니다.
    cursor.execute('''
        INSERT INTO subscriptions (endpoint, data) 
        VALUES (?, ?)
        ON CONFLICT(endpoint) DO UPDATE SET data=excluded.data
    ''', (endpoint, data_str))
    conn.commit()
    conn.close()

def get_all_subscriptions():
    """
    데이터베이스에 저장된 모든 구독 정보를 리스트 형태로 반환합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscriptions')
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

def delete_subscription(subscription_id):
    """
    ID를 기준으로 특정 구독 정보를 데이터베이스에서 삭제합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscriptions WHERE id = ?', (subscription_id,))
    conn.commit()
    conn.close()

def delete_subscription_by_endpoint(endpoint):
    """
    endpoint URL을 기준으로 특정 구독 정보를 데이터베이스에서 삭제합니다.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscriptions WHERE endpoint = ?', (endpoint,))
    conn.commit()
    conn.close()
    print(f"구독 정보 삭제됨: {endpoint}")

