import calendar
import hashlib
from datetime import date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, redirect, render_template, request, session

from tutortime.models import Lesson, LessonStatus, ServiceStatus, User

user_bp = Blueprint("user", __name__)
statuses = [
    LessonStatus.ACCEPTED,
    LessonStatus.ACCEPTED_STUDENT,
    LessonStatus.ACCEPTED_TUTOR,
    LessonStatus.CONFIRMED,
    LessonStatus.CONFIRMED_STUDENT,
    LessonStatus.CONFIRMED_TUTOR,
]


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


@user_bp.route("/user/account/list")
def user_account_list():
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="view your profile")

    user = User.get(session["user_id"])
    services = user.get_services(ServiceStatus.ACTIVE)
    lessons = [lesson.to_json() for lesson in Lesson.get_lessons_for_user(user.id, statuses, False)]

    minutes = user.minutes
    for lesson in lessons:
        lesson["balance"] = minutes
        if lesson["tutor_id"] == session["user_id"] and lesson["status"] == LessonStatus.CONFIRMED:
            minutes -= lesson["actual_duration"]
        elif lesson["student_id"] == session["user_id"] and lesson["status"].startswith("accepted_") is False:
            minutes += lesson["proposed_duration"]
    return render_template("user/account/list.html", user=user, services=services, lessons=lessons)


@user_bp.route("/user/calendar/list")
def user_calendar_list():
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="view your calendar")

    lessons = list(Lesson.get_lessons_for_user(session["user_id"], statuses))

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
            if cur_month.month == lesson.lesson_ts.month and cur_month.year == lesson.lesson_ts.year:
                month["lessons"].append(lesson.to_json())
        cal.append(month)

    return render_template("user/calendar/list.html", lessons=lessons, calendar=cal, today=today.day)
