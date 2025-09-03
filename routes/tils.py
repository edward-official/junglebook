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
  
  try:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
  except ValueError:
    return jsonify({"error": "invalid date format, expected YYYY-MM-DD"})
  
  start = date_obj
  end = date_obj + timedelta(days=1)
  documents = database.tils.find(
    {"createdAt": {"$gte": start, "$lt": end}},
    {"_id": 0, "username": 1, "url": 1, "createdAt": 1, "updatedAt": 1}
  )

  response_data = []
  for document in documents:
    response_data.append({
      "userName": document.get("username"),
      "url": document.get("url"),
      "createdAt": document.get("createdAt").strftime("%Y-%m-%d %H:%M:%S") if document.get("createdAt") else None,
      "updatedAt": document.get("updatedAt").strftime("%Y-%m-%d %H:%M:%S") if document.get("updatedAt") else None
    })
  return jsonify({"data": response_data})

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

@tils_bp.route("/commit", methods=["POST"])
@jwt_required()
def commit():
  print("🚨 check point committing TIL")
  current_user = get_jwt_identity()
  user_name = current_user
  url = request.form.get("url")
  date_str = request.form.get("date")
  print(date_str)
  commit_date = datetime.fromisoformat(date_str)

  start_of_day = datetime(commit_date.year, commit_date.month, commit_date.day)
  end_of_day = datetime(commit_date.year, commit_date.month, commit_date.day, 23, 59, 59)

  database = current_app.config["DB"]
  existing = database.tils.find_one({
    "username": user_name,
    "createdAt": {"$gte": start_of_day, "$lte": end_of_day}
  })
  # print("🚨 " + existing)

  if existing:
    database.tils.update_one(
      {"_id": existing["_id"]},
      {"$set": {
        "updatedAt": datetime.now(timezone.utc),
        "url": url
      }}
    )
    return jsonify({"result": "success", "status": "updated"})
  else:
    database.tils.insert_one({
      "username": user_name,
      "learnedDate": date_str,
      "createdAt": commit_date,
      "updatedAt": None,
      "url": url
    })
    return jsonify({"result": "success", "status": "created"})