import calendar
import hashlib
from datetime import date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, abort, redirect, render_template, request, session
from models import Lesson, User

# from ..services.models import LessonStatus, ServiceStatus

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/account/login", methods=["GET", "POST"])
def user_account_login():
    if request.method == "GET":
        if session.get("user_id") is not None:
            return redirect("/service/list/")
        return render_template("user/account/login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            return render_template("user/account/login.html", error_msg="Please provide a username and password")

        user = User.get_by_creds(username, password)
        if user is None:
            return render_template("user/account/login.html", error_msg="Invalid credentials, try again")

        session["user_id"] = user.id
        return redirect("/service/list/")


@user_bp.route("/user/account/logout")
def user_account_logout():
    if session.get("user_id") is not None:
        del session["user_id"]
    return redirect("/service/list/")


@user_bp.route("/user/account/create", methods=["GET", "POST"])
def user_account_create():
    if request.method == "GET":
        if session.get("user_id") is not None:
            return redirect("/service/list/")
        return render_template("user/account/create.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            return render_template("user/account/create.html", error_msg="Please provide a username and password")

        encoded_password = hashlib.sha256(password.encode()).hexdigest()
        user = User(username=username, password=encoded_password, timezone="America/Toronto")
        if user.add() is False:
            return render_template("user/account/create.html", error_msg="User account already exists")

        session["user_id"] = user.id
        return redirect("/service/list/")


# @user_bp.route("/user/account/list")
# def user_account_list():
#     if "username" not in session:
#         return render_template("error/not_logged_in.html")

#     services = db.get_services_by_status(session["userId"], ServiceStatus.ACTIVE)
#     lessons = db.get_lessons_for_user(session["userId"])
#     balance = db.get_user_balance(session["userId"])
#     original_balance = balance
#     for lesson in lessons:
#         dt = datetime.strptime(lesson["datetime"], "%Y-%m-%dT%H:%M")
#         lesson["day"] = datetime.strftime(dt, "%d/%m/%Y")
#         lesson["tutorName"] = db.get_username(lesson["tutorId"])
#         lesson["studentName"] = db.get_username(lesson["studentId"])
#         if lesson["tutorId"] == session["userId"] and lesson["status"] == LessonStatus.CONFIRMED:
#             lesson["balance"] = balance
#             balance -= lesson["actualDurationMinutes"]
#         elif lesson["studentId"] == session["userId"] and lesson["status"].startswith("accepted_") == False:
#             lesson["balance"] = balance
#             balance += lesson["proposedDurationMinutes"]
#         else:
#             lesson["balance"] = balance

#     return render_template(
#         "user/account/list.html",
#         user_id=session["userId"],
#         services=services,
#         lessons=lessons,
#         balance=original_balance,
#     )


@user_bp.route("/user/calendar/list")
def user_calendar_list():
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="view your calendar")

    lessons = list(Lesson.get_for_user(session["user_id"]))

    cal = []
    today = date.today()
    for i in range(-12, 13):
        cur_month = today + relativedelta(months=i)
        monthrange = calendar.monthrange(cur_month.year, cur_month.month)
        month = {}
        month["year"] = cur_month.year
        month["month"] = cur_month.month
        month["month_name"] = calendar.month_name[cur_month.month]
        month["month_offset"] = monthrange[0]
        month["month_length"] = monthrange[1]
        month["lessons"] = []
        for lesson in lessons:
            if cur_month.month == lesson.timestamp.month and cur_month.year == lesson.timestamp.year:
                month["lessons"].append(lesson.to_json())
        cal.append(month)

    return render_template("user/calendar/list.html", lessons=lessons, calendar=cal, today=today.day)