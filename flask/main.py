from flask import Flask, session, render_template, request
from database import Database

app = Flask(__name__)
app.config.from_object('config')

db = Database("db/user.sqlite", "db/service.sqlite") 

@app.route("/")
def root():
    return render_template("home.html")


@app.route("/resources")
def resources():
    pass

@app.route("/about")
def about():
    pass

@app.route("/service/list")
def service_list():
    return render_template("/service/list.html")

@app.route("/user/account/auth", methods = ["GET", "POST"])
def user_account_auth():
    if request.method == "GET":
        if "username" in session:
            return render_template("home.html")
        return render_template("user/account/auth.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or password is None or db.verify_login(username, password) == False:
            if username is None or password is None:
                failure_msg = "Please provide a username and password"
            else:
                failure_msg = "Invalid credentials, try again"
            return render_template("user/account/auth.html", failure_msg = failure_msg)
        session["username"] = request.form.get("username")
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
        services = db.get_services(session["username"], status)
        return render_template("user/service/list.html", services = services, status=status)
    return render_template("user/service/list.html", status=status)

@app.route("/user/service/create", methods = ["GET", "POST"])
def user_service_create():
    if "username" not in session:
        return render_template("user/account/auth.html")
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