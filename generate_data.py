from pymongo import MongoClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os, bcrypt, pytz, random

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
users = db.users
tils = db.tils

sample_users = [
  {"username": "홍길동(정글11기-01)", "userid": "jungle11number01", "password": "jungle11number01"},
  {"username": "김영희(정글11기-02)", "userid": "jungle11number02", "password": "jungle11number02"},
  {"username": "이철수(정글11기-03)", "userid": "jungle11number03", "password": "jungle11number03"},
  {"username": "박민수(정글11기-04)", "userid": "jungle11number04", "password": "jungle11number04"},
  {"username": "최지현(정글11기-05)", "userid": "jungle11number05", "password": "jungle11number05"},
  {"username": "강하늘(정글11기-06)", "userid": "jungle11number06", "password": "jungle11number06"},
  {"username": "윤서준(정글11기-07)", "userid": "jungle11number07", "password": "jungle11number07"},
  {"username": "정수빈(정글11기-08)", "userid": "jungle11number08", "password": "jungle11number08"},
  {"username": "오준호(정글11기-09)", "userid": "jungle11number09", "password": "jungle11number09"},
  {"username": "한예진(정글11기-10)", "userid": "jungle11number10", "password": "jungle11number10"},
  {"username": "서지호(정글11기-11)", "userid": "jungle11number11", "password": "jungle11number11"},
  {"username": "배도현(정글11기-12)", "userid": "jungle11number12", "password": "jungle11number12"},
  {"username": "장유나(정글11기-13)", "userid": "jungle11number13", "password": "jungle11number13"},
  {"username": "임재혁(정글11기-14)", "userid": "jungle11number14", "password": "jungle11number14"},
  {"username": "문가영(정글11기-15)", "userid": "jungle11number15", "password": "jungle11number15"},
  {"username": "하준석(정글11기-16)", "userid": "jungle11number16", "password": "jungle11number16"},
  {"username": "조민지(정글11기-17)", "userid": "jungle11number17", "password": "jungle11number17"},
  {"username": "백승현(정글11기-18)", "userid": "jungle11number18", "password": "jungle11number18"},
  {"username": "노하린(정글11기-19)", "userid": "jungle11number19", "password": "jungle11number19"},
  {"username": "유지호(정글11기-20)", "userid": "jungle11number20", "password": "jungle11number20"},
]

def hash_pw(pw: str) -> str:
  return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def insert_users():
  users.delete_many({})
  documents_insert = []
  for sample_user in sample_users:
    documents_insert.append({
      "username": sample_user["username"],
      "userid": sample_user["userid"],
      "password": hash_pw(sample_user["password"]),
      "last_login": None
    })
  response_insert = users.insert_many(documents_insert)
  print(len(response_insert.inserted_ids))


kst = pytz.timezone("Asia/Seoul")
start_time = kst.localize(datetime(2025, 8, 31, 0, 0, 0))
end_time = kst.localize(datetime(2025, 9, 4, 17, 0, 0))
user_ids = [f"jungle11number{i:02d}" for i in range(1, 21)]

def insert_tils():
  tils.delete_many({})
  docs = []
  last_streak = {}
  last_date = {}
  current_time = start_time
  while current_time <= end_time:
    learned_date = current_time.strftime("%Y-%m-%d")
    base_utc = current_time.astimezone(pytz.utc)
    for idx, uid in enumerate(user_ids, start=1):
      prob = 5 * idx
      if random.randint(1, 100) > prob:
        continue
      delta_hours = random.uniform(10, 50)
      created_at = base_utc + timedelta(hours=delta_hours)
      if created_at > end_time.astimezone(pytz.utc):
        continue
      is_commit_on_time = created_at <= base_utc + timedelta(hours=24)
      if not is_commit_on_time:
        streak = 0
      else:
        prev_date = (current_time - timedelta(days=1)).date()
        if last_date.get(uid) == prev_date:
          streak = last_streak.get(uid, 0) + 1
        else:
          streak = 1
      last_streak[uid] = streak
      last_date[uid] = current_time.date()
      docs.append({
        "username": uid,
        "learnedDate": learned_date,
        "createdAt": created_at,
        "updatedAt": None,
        "url": "https://naver.com",
        "isCommitOnTime": is_commit_on_time,
        "streak": streak
      })
    current_time += timedelta(days=1)
  if docs:
    res = tils.insert_many(docs)
    print(f"{len(res.inserted_ids)} tils inserted")
  else:
    print("0 tils inserted")



if __name__ == "__main__":
  insert_users()
  insert_tils()
