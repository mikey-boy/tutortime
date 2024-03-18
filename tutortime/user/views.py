import calendar
import hashlib
import json
from datetime import date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, Flask, redirect, render_template, request, session, url_for
from rauth import OAuth2Service

from tutortime.models import Lesson, LessonStatus, ServiceStatus, User
from tutortime.user.utils import availability_to_int, availability_to_list

google = None
facebook = None
user_bp = Blueprint("user", __name__)
statuses = [
    LessonStatus.ACCEPTED,
    LessonStatus.ACCEPTED_STUDENT,
    LessonStatus.ACCEPTED_TUTOR,
    LessonStatus.CONFIRMED,
    LessonStatus.CONFIRMED_STUDENT,
    LessonStatus.CONFIRMED_TUTOR,
]


def configure_oauth_providers(app: Flask):
    global google
    google = OAuth2Service(
        name="google",
        client_id=app.config["GOOGLE_OAUTH"]["client_id"],
        client_secret=app.config["GOOGLE_OAUTH"]["client_secret"],
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        access_token_url="https://oauth2.googleapis.com/token",
    )

    global facebook
    facebook = OAuth2Service(
        name="facebook",
        client_id=app.config["FACEBOOK_OAUTH"]["client_id"],
        client_secret=app.config["FACEBOOK_OAUTH"]["client_secret"],
        authorize_url="https://graph.facebook.com/oauth/authorize",
        access_token_url="https://graph.facebook.com/oauth/access_token",
        base_url="https://graph.facebook.com/",
    )


@user_bp.route("/user/account/login")
def user_account_login():
    if session.get("user_id") is not None:
        return redirect("/service/list/")
    return render_template("user/account/login.html")


@user_bp.route("/user/account/local", methods=["GET", "POST"])
def user_account_local():
    if request.method == "GET":
        if session.get("user_id") is not None:
            return redirect("/service/list/")
        return render_template("user/account/local.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            return render_template("user/account/local.html", error_msg="Please provide a username and password")

        user = User.get_by_creds(username, password)
        if user is None:
            return render_template("user/account/local.html", error_msg="Invalid credentials, try again")

        session["user_id"] = user.id
        return redirect("/service/list/")


@user_bp.route("/user/account/update", methods=["POST"])
def user_account_update():
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="edit your profile")

    user = User.get(session["user_id"])

    username = request.form.get("username")
    description = request.form.get("description")
    availability = availability_to_int(request.form.keys())
    images = request.files.getlist("images")

    error_msg = ""
    status = user.update(username=username, description=description, availability=availability, images=images)
    if status == -1:
        error_msg = "Display name is a required field"
    elif status == -2:
        error_msg = "Display name already taken"

    return render_template(
        "/user/account/list.html", user=user, availability=availability_to_list(availability), error_msg=error_msg
    )


def add_or_get_user(social_id):
    from random import randint

    user = User.get_by_social_id(social_id)
    if user is None:
        username = f"user{randint(1, 1000000)}"
        user = User(social_id=social_id, username=username, timezone="America/Toronto")
        user.add()
        return user, True
    return user, False


@user_bp.route("/user/callback/facebook")
def user_callback_facebook():
    def decode_json(payload):
        return json.loads(payload.decode("utf-8"))

    if "code" not in request.args:
        return None, None, None

    redirect_url = url_for("user.user_callback_facebook", _external=True)
    data = {"code": request.args["code"], "grant_type": "authorization_code", "redirect_uri": redirect_url}
    oauth_session = facebook.get_auth_session(data=data, decoder=decode_json)
    response = oauth_session.get("me")
    if response.status_code == 200:
        social_id = f"facebook${response.json()['id']}"
        user, added = add_or_get_user(social_id=social_id)
        session["user_id"] = user.id
        if added:
            return redirect("/user/account/update")

    return redirect("/service/list/")


@user_bp.route("/user/authorize/facebook")
def user_authorize_facebook():
    redirect_url = url_for("user.user_callback_facebook", _external=True)
    return redirect(facebook.get_authorize_url(scope="email", response_type="code", redirect_uri=redirect_url))


@user_bp.route("/user/callback/google")
def user_callback_google():
    if "code" not in request.args:
        return None, None, None

    redirect_uri = url_for("user.user_callback_google", _external=True)
    data = {"code": request.args["code"], "grant_type": "authorization_code", "redirect_uri": redirect_uri}
    oauth_session = google.get_auth_session(data=data, decoder=json.loads)

    params = {"personFields": "emailAddresses"}
    response = oauth_session.get("https://www.googleapis.com/oauth2/v1/userinfo", params=params)
    if response.status_code == 200:
        social_id = f"google${response.json()['id']}"
        user, added = add_or_get_user(social_id=social_id)
        session["user_id"] = user.id
        if added:
            return redirect("/user/account/update")

    return redirect("/service/list/")


@user_bp.route("/user/authorize/google")
def user_authorize_google():
    redirect_uri = url_for("user.user_callback_google", _external=True)
    return redirect(google.get_authorize_url(scope="email", response_type="code", redirect_uri=redirect_uri))


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

        social_id = f"local${username}"
        encoded_password = hashlib.sha256(password.encode()).hexdigest()
        user = User(social_id=social_id, username=username, password=encoded_password, timezone="America/Toronto")
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
            if lesson["bonus_duration"] != 0:
                minutes -= lesson["bonus_duration"]
        elif lesson["student_id"] == session["user_id"] and lesson["status"].startswith("accepted_") is False:
            minutes += lesson["proposed_duration"]
    return render_template("user/account/list.html", user=user, services=services, lessons=lessons)


@user_bp.route("/user/account/display/<int:user_id>")
def user_account_display(user_id: str):
    user = User.get(user_id)
    if user is None:
        return render_template("error/nonexistant_user.html")

    services = user.get_services(ServiceStatus.ACTIVE)
    lessons = []
    for service in services:
        lessons.append([lesson for lesson in service.lessons if lesson.status == LessonStatus.CONFIRMED])

    return render_template("user/account/display.html", user=user, services=services, lessons=lessons)


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
