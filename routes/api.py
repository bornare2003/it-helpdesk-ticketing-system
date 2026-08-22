from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_

from models import db, Ticket

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _validate_payload(data, partial=False):
    """Validate incoming ticket JSON. Returns (errors_dict, cleaned_data)."""
    errors = {}
    cleaned = {}
    cfg = current_app.config

    required_fields = ["title", "description", "category", "priority", "requester_name", "requester_email"]
    if not partial:
        for field in required_fields:
            if not data.get(field):
                errors[field] = "This field is required."

    if "title" in data:
        title = (data.get("title") or "").strip()
        if title:
            cleaned["title"] = title[:150]

    if "description" in data:
        desc = (data.get("description") or "").strip()
        if desc:
            cleaned["description"] = desc

    if "category" in data:
        category = data.get("category")
        if category and category not in cfg["CATEGORIES"]:
            errors["category"] = f"Must be one of {cfg['CATEGORIES']}"
        elif category:
            cleaned["category"] = category

    if "priority" in data:
        priority = data.get("priority")
        if priority and priority not in cfg["PRIORITIES"]:
            errors["priority"] = f"Must be one of {cfg['PRIORITIES']}"
        elif priority:
            cleaned["priority"] = priority

    if "status" in data:
        status = data.get("status")
        if status and status not in cfg["STATUSES"]:
            errors["status"] = f"Must be one of {cfg['STATUSES']}"
        elif status:
            cleaned["status"] = status

    if "requester_name" in data:
        name = (data.get("requester_name") or "").strip()
        if name:
            cleaned["requester_name"] = name[:100]

    if "requester_email" in data:
        email = (data.get("requester_email") or "").strip()
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                errors["requester_email"] = "Must be a valid email address."
            else:
                cleaned["requester_email"] = email[:150]

    return errors, cleaned


@api_bp.route("/tickets", methods=["GET"])
def list_tickets():
    query = Ticket.query

    category = request.args.get("category")
    priority = request.args.get("priority")
    status = request.args.get("status")
    search = request.args.get("search", "").strip()

    if category and category != "All":
        query = query.filter(Ticket.category == category)
    if priority and priority != "All":
        query = query.filter(Ticket.priority == priority)
    if status and status != "All":
        query = query.filter(Ticket.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.title.ilike(like),
                Ticket.description.ilike(like),
                Ticket.requester_name.ilike(like),
                Ticket.requester_email.ilike(like),
            )
        )

    sort = request.args.get("sort", "created_desc")
    sort_map = {
        "created_desc": Ticket.created_at.desc(),
        "created_asc": Ticket.created_at.asc(),
        "priority": Ticket.priority.asc(),
        "status": Ticket.status.asc(),
    }
    query = query.order_by(sort_map.get(sort, Ticket.created_at.desc()))

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "tickets": [t.to_dict() for t in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page,
    })


@api_bp.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict())


@api_bp.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_payload(data, partial=False)
    if errors:
        return jsonify({"errors": errors}), 400

    ticket = Ticket(
        title=cleaned["title"],
        description=cleaned["description"],
        category=cleaned["category"],
        priority=cleaned["priority"],
        status=cleaned.get("status", "Open"),
        requester_name=cleaned["requester_name"],
        requester_email=cleaned["requester_email"],
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket.to_dict()), 201


@api_bp.route("/tickets/<int:ticket_id>", methods=["PUT", "PATCH"])
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json(silent=True) or {}
    errors, cleaned = _validate_payload(data, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400

    for key, value in cleaned.items():
        setattr(ticket, key, value)

    db.session.commit()
    return jsonify(ticket.to_dict())


@api_bp.route("/tickets/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket #{ticket_id} deleted."}), 200


@api_bp.route("/stats", methods=["GET"])
def stats():
    total = Ticket.query.count()
    by_status = {
        s: Ticket.query.filter_by(status=s).count() for s in current_app.config["STATUSES"]
    }
    by_priority = {
        p: Ticket.query.filter_by(priority=p).count() for p in current_app.config["PRIORITIES"]
    }
    by_category = {
        c: Ticket.query.filter_by(category=c).count() for c in current_app.config["CATEGORIES"]
    }
    return jsonify({
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
    })


@api_bp.route("/meta", methods=["GET"])
def meta():
    cfg = current_app.config
    return jsonify({
        "categories": cfg["CATEGORIES"],
        "priorities": cfg["PRIORITIES"],
        "statuses": cfg["STATUSES"],
    })