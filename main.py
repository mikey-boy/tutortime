from flask import Flask, session, render_template, request, jsonify, redirect
from database import Database
from image_server import ImageServer
from utils import availability_to_int, availability_to_list
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config.from_object('config')

db = Database(db_folder=app.config['DB_FOLDER'], user_db=app.config['USER_DB'], service_db=app.config['SERVICE_DB']) 
image_server = ImageServer(image_folder=app.config['IMAGE_FOLDER'])

@app.route("/")
def root():
    return service_list()

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/user/account/login", methods = ["GET", "POST"])
def user_account_login():
    if request.method == "GET":
        if "username" in session:
            return redirect('/user/service/list/active')
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
        session["username"] = username
        session["userId"] = db.get_user_id(username)
        return redirect('/service/list/')

@app.route("/user/account/logout")
def user_account_logout():
    if "username" in session:
        del session["username"]
    return redirect('/service/list/')

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
        user_id = db.add_user(username, password)
        session["username"] = username
        session["userId"] = user_id
        return render_template("home.html")

@app.route("/api/service/list/<string:category>")
def api_service_list(category="all"):
    services = db.get_all_services_by_category(category)
    json_services = [dict(service) for service in services]
    for json_service in json_services:
        images = db.get_images_by_service_id(json_service['id'])
        json_service['images'] = [{'filenameOnServer': image['filenameOnServer'], 'filename': image['filename']} for image in images]
    return jsonify(json_services)

@app.route("/service/list/")
@app.route("/service/list/<int:service_id>")
def service_list(service_id=None):
    if service_id:
        service = db.get_service_by_id(service_id)
        images = db.get_images_by_service_id(service_id)
        json_service = dict(service)
        json_service["available"] = availability_to_list(json_service["availability"])
        json_service['images'] = [{'filenameOnServer': image['filenameOnServer'], 'filename': image['filename']} for image in images]
        return render_template("service/display.html", service=json_service)
    else:
        services = db.get_all_services()
        json_services = [dict(service) for service in services]
        for json_service in json_services:
            images = db.get_images_by_service_id(json_service['id'])
            json_service['images'] = [{'filenameOnServer': image['filenameOnServer'], 'filename': image['filename']} for image in images]
        return render_template("service/list.html", services=json_services)

@app.route("/service/booking/create/<int:service_id>", methods = ["POST"])
def service_booking_create(service_id):
    if "userId" in session:
        service = db.get_service_by_id(service_id)
        datetime = request.form.get("datetime")
        duration = request.form.get("duration")
        db.add_booking(service["id"], service["userId"], session["userId"], datetime, duration)
        return render_template("home.html")


@app.route("/api/user/service/list/<string:status>")
def api_user_service_list(status="active"):
    if "username" in session:
        services = db.get_services_by_status(session["username"], status)
        json_services = [dict(service) for service in services]
        return jsonify(json_services)
    return jsonify([])

@app.route("/user/service/list/<string:status>")
def user_service_list(status="active"):
    if "username" in session:
        services = db.get_services_by_status(session["username"], status)
        return render_template("user/service/list.html", services=services, status=status)
    return render_template("user/service/list.html")

@app.route("/user/service/create", methods = ["GET", "POST"])
def user_service_create():
    if "username" not in session:
        return render_template("user/account/login.html")
    if request.method == "GET":
        return render_template("user/service/create.html", service={})
    else: 
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        if title is None or description is None or category is None:
            failure_msg = "Please provide all the required fields"
            return ("user/service/create.html", failure_msg)
        
        availability = availability_to_int(request.form.keys())
        images = request.files.getlist("images")
        files = image_server.store_images(images)
        db.add_service(session["username"], session["userId"], title, description, category, availability, files)
        return redirect('/user/service/list/active')

@app.route("/user/service/delete/<int:service_id>")
def user_service_delete(service_id):
    result = db.get_service_by_id(service_id)
    if result["username"] == session["username"]:
        images = db.get_images_by_service_id(service_id)
        image_server.remove_images(images)
        db.remove_service(session["username"], service_id)
        return redirect(f'/user/service/list/{result["status"]}')

@app.route("/user/service/update/<int:service_id>", methods = ["GET", "POST"])
def user_service_update(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    
    service = db.get_service_by_id(service_id)
    if service["username"] != session["username"]:
        return render_template("home.html")
    
    if request.method == "GET":
        service = dict(service)
        service["available"] = availability_to_list(service["availability"])
        return render_template("user/service/create.html", service = service)
    else:
        old_images = db.get_images_by_service_id(service_id)
        image_server.remove_images(old_images)

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        availability = availability_to_int(request.form.keys())
        images = request.files.getlist("images")
        files = image_server.store_images(images)
        result = db.update_service(session["username"], service_id, title, description, category, availability, files)
        return redirect(f'/user/service/list/{result["status"]}')

@app.route("/user/service/pause/<int:service_id>")
def user_service_pause(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.pause_service(session["username"], service_id)
    return redirect('/user/service/list/active')

@app.route("/user/service/activate/<int:service_id>")
def user_service_activate(service_id):
    if "username" not in session:
        return render_template("user/account/login.html")
    db.activate_service(session["username"], service_id)
    return redirect('/user/service/list/paused')

@app.route("/user/messages/list")
def user_messages_list():
    return render_template("user/messages/list.html")

@app.route("/user/calendar/list")
def user_calendar_list():
    if "username" not in session:
        return render_template("user/calendar/list.html", services = [])
    rows = db.get_bookings_for_user(session["userId"])

    services = [dict(row) for row in rows]
    for service in services:
        dt = datetime.strptime(service["datetime"], "%Y-%m-%dT%H:%M")
        offset = date(dt.year, dt.month, 1).weekday() 
        service["row"] = ((dt.day + offset) // 7) + 2
        service["column"] = (dt.day + offset) % 7

    calendars = []
    today = date.today()
    # for i in range(-12, 13):
    for i in range(2):
        d = today - relativedelta(months=i)
        tmp = {}
        tmp["offset"] = date(d.year, d.month, 1).weekday()
        tmp["month"] = d.month
        tmp["year"] = d.year
        calendars.append(tmp)
    print(calendars)
    return render_template("user/calendar/list.html", services = services, calendars=calendars)