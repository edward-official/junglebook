import html
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone, timedelta
tils_bp = Blueprint('tils', __name__, url_prefix='/tils')

@tils_bp.route('/day', methods=['GET'])
@jwt_required()
def day():
  database = current_app.config['DB']
  date_str = request.args.get("date")
  
  if not date_str:
    return jsonify({"error": "date parameter is required"})

  tils = database.tils.find(
    {"learnedDate": date_str},
    {"_id": 0, "username": 1, "url": 1, "createdAt": 1, "updatedAt": 1}
  )

  response_data = []
  for til in tils:
    user_name = database.users.find_one({"userid": til.get("username")}, {"_id": 0}).get("username")
    response_data.append({
      "userName": user_name,
      "url": html.escape(til.get("url") or ""),
      "createdAt": til.get("createdAt").strftime("%Y-%m-%d %H:%M:%S") if til.get("createdAt") else None,
      "updatedAt": til.get("updatedAt").strftime("%Y-%m-%d %H:%M:%S") if til.get("updatedAt") else None
    })
  return jsonify({"data": response_data})

@tils_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def heatmap():
  number_of_total_users = len(list(current_app.config["DB"].users.find({}, {"_id": 0})))
  pipeline = [
    {"$group": {"_id": "$learnedDate", "numberOfPosts": {"$sum": 1}}},
    {"$project": {"date": "$_id", "numberOfPosts": 1, "_id": 0}},
    {"$sort": {"date": 1}}
  ]
  data = list(current_app.config["DB"].tils.aggregate(pipeline))

  return jsonify({
    "totalUser": number_of_total_users,
    "data": data,
  })

@tils_bp.route("/commit", methods=["POST"])
@jwt_required()
def commit():
  current_user = get_jwt_identity()
  user_name = current_user

  url = request.form.get("url")

  learned_date = request.form.get("date")
  commit_date = datetime.now()

  database = current_app.config["DB"]
  existing = database.tils.find_one({
    "username": user_name,
    "learnedDate": learned_date
  })

  if existing:
    database.tils.update_one(
      {"_id": existing["_id"]},
      {"$set": {
        "updatedAt": datetime.now(),
        "url": url,
      }}
    )
    return jsonify({"result": "success", "status": "updated"})
  else:
    learned_date_obj = datetime.strptime(learned_date, "%Y-%m-%d").date()
    previous_date_obj = learned_date_obj - timedelta(days=1)
    previous_date_str = previous_date_obj.strftime("%Y-%m-%d")
    previous_til = database.tils.find_one({
      "username": user_name,
      "learnedDate": previous_date_str,
      "isCommitOnTime": True,
    })
    previous_streak = previous_til.get("streak") if previous_til else 0

    is_commit_on_time = datetime.strptime(learned_date, "%Y-%m-%d").date()==commit_date.date()
    streak = previous_streak + 1 if is_commit_on_time else 0

    database.tils.insert_one({
      "username": user_name,
      "learnedDate": learned_date,
      "createdAt": commit_date,
      "updatedAt": None,
      "url": url,
      "isCommitOnTime": is_commit_on_time,
      "streak": streak,
    })
    return jsonify({"result": "success", "status": "created"})