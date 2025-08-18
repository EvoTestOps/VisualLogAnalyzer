from flask import Blueprint, redirect

dash_redirects_bp = Blueprint("redirects", __name__)


@dash_redirects_bp.route("/")
def home():
    return redirect("/dash")


# TODO: Move somewere else
@dash_redirects_bp.route("/health")
def health():
    return "OK", 200
