from flask import Blueprint, redirect, render_template, request, session
from models import User

# from ..services.models import LessonStatus, ServiceStatus

users_bp = Blueprint("users", __name__)


@users_bp.route("/user/account/login", methods=["GET", "POST"])
def user_account_login():
    if request.method == "GET":
        if "username" in session:
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


@users_bp.route("/user/account/logout")
def user_account_logout():
    if "user_id" in session:
        del session["user_id"]
    return redirect("/service/list/")


@users_bp.route("/user/account/create", methods=["GET", "POST"])
def user_account_create():
    if request.method == "GET":
        if "user" in session:
            return redirect("/service/list/")
        return render_template("user/account/create.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            return render_template("user/account/create.html", error_msg="Please provide a username and password")

        user = User(username=username, password=password, timezone="America/Toronto")
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
