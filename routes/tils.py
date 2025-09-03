from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
tils_bp = Blueprint('tils', __name__, url_prefix='/tils')

# @tils_bp.route('/day', methods=['GET'])
# @jwt_required()
# def day():
#   # 해당일의 모든 til 내역을 반환 > 잔디, hover, 내역생성
#   day = request.form.get["date"]
#   database = current_app.config['DB']
#   users = database.users
#   return

@tils_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def heatmap():
  number_of_total_users = len(list(current_app.config["DB"].users.find({}, {"_id": 0})))
  pipeline = [
    {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}}, "numberOfPosts": {"$sum": 1}}},
    {"$project": {"date": "$_id", "numberOfPosts": 1, "_id": 0}},
    {"$sort": {"date": 1}}
  ]
  data = list(current_app.config["DB"].tils.aggregate(pipeline))

  return jsonify({
    "totalUser": number_of_total_users,
    "data": data,
  })

@tils_bp.route("/commit", methods=["GET"])
@jwt_required()
def commit():
  current_user = get_jwt_identity()
  user_name = current_user
  url = request.form.get("url")
  date_str = request.form.get("date")
  commit_date = datetime.fromisoformat(date_str)

  start_of_day = datetime(commit_date.year, commit_date.month, commit_date.day)
  end_of_day = datetime(commit_date.year, commit_date.month, commit_date.day, 23, 59, 59)

  database = current_app.config["DB"]
  existing = database.tils.find_one({
    "username": user_name,
    "createdAt": {"$gte": start_of_day, "$lte": end_of_day}
  })

  if existing:
    database.tils.update_one(
      {"_id": existing["_id"]},
      {"$set": {
        "updatedAt": datetime.now(timezone.utc),
        "url": url
      }}
    )
    return jsonify({"message": "TIL updated", "status": "updated"})
  else:
    database.tils.insert_one({
      "username": user_name,
      "createdAt": commit_date,
      "updatedAt": None,
      "url": url
    })
    return jsonify({"message": "TIL created", "status": "created"})