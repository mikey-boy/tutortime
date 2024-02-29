from flask import Blueprint, render_template

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/docs/privacy")
def docs_privacy():
    return render_template("docs/privacy.html")
