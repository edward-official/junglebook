from datetime import datetime, timedelta, timezone
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from zoneinfo import ZoneInfo

render_blueprint = Blueprint("main", __name__, url_prefix="/")

@render_blueprint.route("/")
@jwt_required(optional=True)
def index():
    current_user = get_jwt_identity()
    if current_user:
        return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("main.login"))

@render_blueprint.route("/login")
def login():
    return render_template("login.html")

@render_blueprint.route("/signup")
def signup():
    return render_template("signup.html")

@render_blueprint.route("/main")
@jwt_required()
def dashboard():
    database = current_app.config["DB"]
    username = get_jwt_identity()
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    today_str = now_kst.strftime("%Y-%m-%d")
    yesterday_str = (now_kst - timedelta(days=1)).strftime("%Y-%m-%d")

    year = now_kst.year
    month = now_kst.month
    days_so_far = now_kst.day

    prefix = f"{year}-{str(month).zfill(2)}"
    numberOfDaysWithCommitThisMonth = len(list(database.tils.find({"username": username, "learnedDate": {"$regex": f"^{prefix}"}}, {"_id": 0})))

    total_user_count = database.users.count_documents({})
    today_til_count = database.tils.count_documents({"learnedDate": today_str})
    yesterday_til_count = database.tils.count_documents({"learnedDate": yesterday_str})

    today_til = database.tils.find_one({"username": username, "learnedDate": today_str},{"_id": 0, "streak": 1})
    streak_today = today_til.get("streak") if today_til else 0
    yesterday_til = database.tils.find_one({"username": username, "learnedDate": yesterday_str},{"_id": 0, "streak": 1})
    streak_yesterday = yesterday_til.get("streak") if yesterday_til else 0

    my_tils = list(database.tils.find({"username": username}, {"_id": 0}))
    my_best_streak = 0
    for til in my_tils:
        streak = til.get("streak", 0)
        if streak > my_best_streak:
            my_best_streak = streak
    """
    [my_streak 구하는 방법]
    1. 내가올린TIL을다가져오기 > 가장 최근 TIL이 오늘 또는 어제인지 확인 > 그렇다면 하루 씩 과거로 움직이면서 TIL이 계속될 때까지 숫자 세기
    2. 따로 구하는 로직이 있을려나
    """
    
    return render_template(
        "main.html",
        my_best_streak = my_best_streak,
        my_streak = max(streak_today, streak_yesterday),
        my_month = f"{numberOfDaysWithCommitThisMonth * 100 / days_so_far}%",
        today_til_count = today_til_count,
        yesterday_til_count = yesterday_til_count,
        total_user_count = total_user_count,
        days_so_far = days_so_far,
        year = year,
        month = month,
    )

@render_blueprint.route("/list")
@jwt_required()
def til_list():
    current_user = get_jwt_identity()
    database = current_app.config['DB']
    date = request.args.get("date")
    today = datetime.now().strftime("%Y-%m-%d")
    if not date or not is_valid_date(date):
        return redirect(url_for("main.til_list", date=today))

    data = database.tils.find_one({"username": current_user, "learnedDate": date})

    return render_template("list.html", url=data["url"] if data else "", isFuture=date > today, date=date)

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
def profile():
    return render_template("list.html")
