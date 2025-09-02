from flask import Blueprint, request, jsonify, current_app
tils_bp = Blueprint('tils', __name__, url_prefix='/tils')

@tils_bp.route('/day', methods=['GET'])
def day():
  # 해당일의 모든 til 내역을 반환 > 잔디, hover, 내역생성
  return

# @tils_bp.route("/", methods=["GET"])