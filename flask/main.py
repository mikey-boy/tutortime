from flask import Flask, session, render_template, request
from database import Database

app = Flask(__name__)
app.config.from_object('config')

db = Database("db/user.sqlite", "db/service.sqlite") 

@app.route("/")
def root():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/service/list")
def service_list():
    services = db.get_all_services()
    return render_template("service/list.html", services = services)

@app.route("/user/account/login", methods = ["GET", "POST"])
def user_account_login():
    if request.method == "GET":
        if "username" in session:
            return render_template("home.html")
        return render_template("user/account/login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None or db.verify_login(username, password) == False:
            if username is None or password is None:
                failure_msg = "Please provide a username and password"
            else:
                failure_msg = "Invalid credentials, try again"
            return render_template("user/account/login.html", failure_msg = failure_msg)
        session["username"] = request.form.get("username")
        return render_template("home.html")

@app.route("/user/account/logout")
def user_account_logout():
    if "username" in session:
        del session["username"]
    return render_template("home.html")

@app.route("/user/account/create", methods = ["GET", "POST"])
def user_account_create():
    if request.method == "GET":
        if "username" in session:
            return render_template("home.html")
        return render_template("user/account/create.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None:
            # TODO show error page
            return render_template("failed_user/account/create.html")
        if db.user_exists(username):
            return render_template("user_exists.html")
        db.add_user(username, password)
        session["username"] = username
        return render_template("home.html")

@app.route("/user/service/list/<string:status>")
def user_service_list(status="active"):
    if "username" in session:
        if status == "active":
            services = db.get_active_services(session["username"])
        elif status == "paused":
            services = db.get_paused_services(session["username"])
        elif status == "draft":
            services = db.get_draft_services(session["username"])
        return render_template("user/service/list.html", services = services, current_status=status, statuses=["active", "draft", "paused"])
    return render_template("user/service/list.html", status=status)

@app.route("/user/service/create", methods = ["GET", "POST"])
def user_service_create():
    if "username" not in session:
        return render_template("user/account/login.html")
    if request.method == "GET":
        return render_template("user/service/create.html")
    else: 
        title = request.form.get("title")
        description = request.form.get("description")
        if title is None or description is None:
            failure_msg = "Please provide all the required fields"
            return ("user/service/create.html", failure_msg)
        db.add_service(session["username"], title, description)
        return user_service_list()

@app.route("/user/service/delete/<int:service_id>")
def user_service_delete(service_id):
    db.remove_service(session["username"], service_id)
    return user_service_list()

@app.route("/user/service/update/<int:service_id>", methods = ["GET", "POST"])
def user_service_update(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    if request.method == "GET":
        service = db.get_service_by_id(session["username"], service_id)
        return render_template("user/service/update.html", service = service)
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        db.update_service(session["username"], service_id, title, description)
        return user_service_list()

@app.route("/user/service/pause/<int:service_id>")
def user_service_pause(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.pause_service(session["username"], service_id)
    return user_service_list(status="paused")

@app.route("/user/service/activate/<int:service_id>")
def user_service_activate(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.activate_service(session["username"], service_id)
    return user_service_list()

@app.route("/user/messages/list")
def user_messages_list():
    return render_template("user/messages/list.html")

@app.route("/user/calendar/list")
def user_calendar_list():
    return render_template("user/calendar/list.html")