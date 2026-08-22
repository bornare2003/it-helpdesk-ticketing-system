"""Seed the database with sample tickets for demo purposes.

Usage:
    python seed.py
"""
import random
from datetime import datetime, timedelta

from app import create_app
from models import db, Ticket

SAMPLE_TICKETS = [
    ("VPN keeps disconnecting", "My VPN connection drops every 10-15 minutes while working from home.", "Network", "High"),
    ("Need Photoshop license", "Requesting a Photoshop license for the design team's new hire.", "Software", "Low"),
    ("Laptop won't boot", "Laptop shows a black screen after the Windows logo. Tried restarting twice.", "Hardware", "High"),
    ("Suspicious phishing email", "Received an email asking to verify my password via a strange link.", "Security", "High"),
    ("Monitor flickering", "External monitor flickers intermittently when connected via HDMI.", "Hardware", "Medium"),
    ("Can't access shared drive", "Getting 'access denied' when opening the Finance shared drive.", "Network", "Medium"),
    ("Outlook crashing on launch", "Outlook crashes immediately after opening since this morning's update.", "Software", "Medium"),
    ("Reset MFA device", "Lost my phone and need to reset multi-factor authentication.", "Security", "High"),
    ("Request second monitor", "Would like a second monitor for my desk setup.", "Hardware", "Low"),
    ("Slow WiFi in conference room B", "WiFi speeds are very slow during meetings in conference room B.", "Network", "Low"),
]

REQUESTERS = [
    ("Aditi Sharma", "aditi.sharma@example.com"),
    ("Rahul Verma", "rahul.verma@example.com"),
    ("Emily Chen", "emily.chen@example.com"),
    ("Michael Brown", "michael.brown@example.com"),
    ("Priya Patel", "priya.patel@example.com"),
]

STATUSES = ["Open", "In Progress", "Resolved"]


def run():
    app = create_app()
    with app.app_context():
        if Ticket.query.count() > 0:
            print("Database already has tickets. Skipping seed.")
            return

        for i, (title, desc, category, priority) in enumerate(SAMPLE_TICKETS):
            name, email = random.choice(REQUESTERS)
            created = datetime.utcnow() - timedelta(days=random.randint(0, 20))
            ticket = Ticket(
                title=title,
                description=desc,
                category=category,
                priority=priority,
                status=random.choice(STATUSES),
                requester_name=name,
                requester_email=email,
                created_at=created,
                updated_at=created,
            )
            db.session.add(ticket)

        db.session.commit()
        print(f"Seeded {len(SAMPLE_TICKETS)} sample tickets.")


if __name__ == "__main__":
    run()