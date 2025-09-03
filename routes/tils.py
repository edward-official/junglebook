from flask import Blueprint, request, jsonify, current_app
tils_bp = Blueprint('tils', __name__, url_prefix='/tils')

@tils_bp.route('/day', methods=['GET'])
def day():
  # 해당일의 모든 til 내역을 반환 > 잔디, hover, 내역생성
  day = request.form.get["date"]
  database = current_app.config['DB']
  users = database.users
  return

@tils_bp.route("/heatmap", methods=["GET"])
def heatmap():
  pipeline = [
    {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$createdAt"}}, "count": {"$sum": 1}}},
    {"$project": {"date": "$_id", "count": 1, "_id": 0}},
    {"$sort": {"date": 1}}
  ]
  return jsonify(list(current_app.config["DB"].tils.aggregate(pipeline)))