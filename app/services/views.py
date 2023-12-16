from flask import Blueprint, abort, redirect, render_template, request, session
from models import Image, Service, ServiceStatus, User
from services.utils import availability_to_int, availability_to_list

services_bp = Blueprint("services", __name__)


@services_bp.route("/")
@services_bp.route("/service/list/")
def service_list():
    services = Service.get_all_services()
    return render_template("service/list.html", services=services)


@services_bp.route("/service/display/<int:service_id>")
def service_display(service_id):
    service = Service.get(service_id)
    user = User.get(service.user)
    if service:
        availability = availability_to_list(service.availability)
        return render_template("service/display.html", service=service, user=user, availability=availability)
    abort(404)


@services_bp.route("/user/service/list/<string:status>")
def user_service_list(status=ServiceStatus.ACTIVE):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html")

    user = User.get(session["user_id"])
    services = user.get_services(status)
    return render_template("user/service/list.html", services=services, status=status)


@services_bp.route("/user/service/create", methods=["GET", "POST"])
def user_service_create():
    if session.get("user_id") is None:
        abort(401)
    if request.method == "GET":
        return render_template("user/service/create.html", service={})
    else:
        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        availability = availability_to_int(request.form.keys())
        if title is None or description is None or category is None:
            error_msg = "Please provide all the required fields"
            return ("user/service/create.html", error_msg)

        service = Service(
            user=session["user_id"], title=title, description=description, category=category, availability=availability
        )
        service.add()

        images = request.files.getlist("images")
        for image in images:
            if image.filename:
                Image(service=service.id, image=image).add()

        return redirect("/user/service/list/active")


@services_bp.route("/user/service/delete/<int:service_id>")
def user_service_delete(service_id):
    if session.get("user_id") is None:
        abort(401)

    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if service:
        status = service.status
        service.remove()
        return redirect(f"/user/service/list/{status}")
    abort(404)


@services_bp.route("/user/service/update/<int:service_id>", methods=["GET", "POST"])
def user_service_update(service_id):
    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if request.method == "GET":
        availability = availability_to_list(service.availability)
        return render_template("user/service/create.html", service=service, availability=availability)
    else:
        for image in service.images:
            image.remove()

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")
        availability = availability_to_int(request.form.keys())
        images = request.files.getlist("images")
        service.update(title, description, category, availability)

        for image in images:
            if image.filename:
                Image(service=service.id, image=image).add()
        return redirect(f"/user/service/list/{service.status}")


def _user_service_status_update(service_id: int, status: ServiceStatus):
    if session.get("user_id") is None:
        abort(401)

    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if service:
        service.update_status(status)
        return redirect(f"/user/service/list/{status}")
    abort(404)


@services_bp.route("/user/service/pause/<int:service_id>")
def user_service_pause(service_id: int):
    return _user_service_status_update(service_id, ServiceStatus.PAUSED)


@services_bp.route("/user/service/activate/<int:service_id>")
def user_service_activate(service_id: int):
    return _user_service_status_update(service_id, ServiceStatus.ACTIVE)
