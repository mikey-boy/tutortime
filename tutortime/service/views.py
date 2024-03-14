from flask import Blueprint, abort, redirect, render_template, request, session

from tutortime.models import Image, Service, ServiceCategory, ServiceStatus, User
from tutortime.service.utils import availability_to_int, availability_to_list

service_bp = Blueprint("service", __name__)


@service_bp.route("/")
@service_bp.route("/service/list/")
def service_list():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    category = request.args.get("category", "", type=str)
    services = Service.get_page(search=search, category=category, page_num=page, per_page=20)

    other_pages = services.iter_pages(left_edge=1, left_current=3, right_current=1, right_edge=1)
    prev_page = services.prev_num
    next_page = services.next_num
    return render_template(
        "service/list.html",
        search=search,
        category=category,
        services=services.items,
        other_pages=other_pages,
        prev_page=prev_page,
        cur_page=page,
        next_page=next_page,
    )


@service_bp.route("/service/display/<int:service_id>")
def service_display(service_id):
    service = Service.get(service_id)
    user = User.get(service.user.id)
    if service:
        availability = availability_to_list(service.availability)
        return render_template("service/display.html", service=service, user=user, availability=availability)
    abort(404)


@service_bp.route("/user/service/list/<string:status>")
def user_service_list(status=ServiceStatus.ACTIVE):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="offer lessons on the site")

    user = User.get(session["user_id"])
    services = user.get_services()
    return render_template("user/service/list.html", services=services, status=status)


@service_bp.route("/user/service/create", methods=["GET", "POST"])
def user_service_create():
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="create a new lesson on the site")
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
            user_id=session["user_id"],
            title=title,
            description=description,
            category=category,
            availability=availability,
        )
        service.add()

        images = request.files.getlist("images")
        if images[0].filename:
            for image in images:
                Image(service_id=service.id, image=image).add()
        else:
            Image(service_id=service.id, category=category).add()

        return redirect("/user/service/list/active")


@service_bp.route("/user/service/update/<int:service_id>", methods=["GET", "POST"])
def user_service_update(service_id):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="update a service on the site")

    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if service:
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

            if images[0].filename:
                for image in images:
                    Image(service_id=service.id, image=image).add()
            else:
                Image(service_id=service.id, category=category).add()
            return redirect(f"/user/service/list/{service.status}")
    abort(404)


@service_bp.route("/user/service/delete/<int:service_id>")
def user_service_delete(service_id):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="delete your lesson on the site")

    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if service:
        status = service.status
        service.remove()
        return redirect(f"/user/service/list/{status}")
    abort(404)


def _user_service_status_update(service_id: int, status: ServiceStatus):
    if session.get("user_id") is None:
        return render_template("error/not_logged_in.html", action="update a service on the site")

    user = User.get(session["user_id"])
    service = user.get_service(service_id)
    if service:
        service.update_status(status)
        return redirect(f"/user/service/list/{status}")
    abort(404)


@service_bp.route("/user/service/pause/<int:service_id>")
def user_service_pause(service_id: int):
    return _user_service_status_update(service_id, ServiceStatus.PAUSED)


@service_bp.route("/user/service/activate/<int:service_id>")
def user_service_activate(service_id: int):
    return _user_service_status_update(service_id, ServiceStatus.ACTIVE)
