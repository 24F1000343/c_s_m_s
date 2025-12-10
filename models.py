from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()

class Principal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(240), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    hods = db.relationship("HOD", backref="department", lazy=True)


class HOD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(240), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    bio = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    availabilities = db.relationship(
        "HODAvailability",
        backref="hod",
        cascade="all, delete-orphan",
        lazy=True
    )

    meetings = db.relationship(
        "Meeting",
        backref="hod",
        cascade="all, delete-orphan",
        lazy=True
    )


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(240), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    meetings = db.relationship(
        "Meeting",
        backref="staff",
        cascade="all, delete-orphan",
        lazy=True
    )


class HODAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hod_id = db.Column(db.Integer, db.ForeignKey("hod.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey("hod.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    agenda = db.Column(db.Text)
    status = db.Column(db.String(30), default="Requested")  # Requested / Approved / Scheduled / Completed / Cancelled

    review = db.relationship(
        "Review",
        backref="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("hod_id", "date", "time", name="unique_hod_meeting_slot"),
    )


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meeting.id"), unique=True)
    summary = db.Column(db.Text)
    improvements = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)


class Blocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # "hod" or "staff"
    ref_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))

class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # <-- NEW
    role = db.Column(db.String(20), nullable=False)   # "hod" or "staff"
    ref_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    date_added = db.Column(db.Date, default=date.today)

