from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(20), nullable=False)   # Hardware / Software / Network / Security
    priority = db.Column(db.String(10), nullable=False)    # Low / Medium / High
    status = db.Column(db.String(15), nullable=False, default="Open")  # Open / In Progress / Resolved

    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(150), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "requester_name": self.requester_name,
            "requester_email": self.requester_email,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
        }

    def __repr__(self):
        return f"<Ticket #{self.id} {self.title!r} [{self.status}]>"