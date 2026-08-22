from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, current_app
)

from models import db, Ticket

views_bp = Blueprint("views", __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("views.admin_login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


@views_bp.route("/")
def index():
    cfg = current_app.config
    return render_template(
        "index.html",
        categories=cfg["CATEGORIES"],
        priorities=cfg["PRIORITIES"],
    )


@views_bp.route("/ticket/<int:ticket_id>")
def ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template("ticket_status.html", ticket=ticket)


@views_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        cfg = current_app.config
        if username == cfg["ADMIN_USERNAME"] and password == cfg["ADMIN_PASSWORD"]:
            session.permanent = True
            session["is_admin"] = True
            session["admin_username"] = username
            next_url = request.args.get("next") or url_for("views.admin_dashboard")
            return redirect(next_url)
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@views_bp.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("views.admin_login"))


@views_bp.route("/admin")
@views_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    cfg = current_app.config
    return render_template(
        "dashboard.html",
        categories=cfg["CATEGORIES"],
        priorities=cfg["PRIORITIES"],
        statuses=cfg["STATUSES"],
        admin_username=session.get("admin_username", "admin"),
    )