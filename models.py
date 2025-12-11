from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------------
# PRINCIPAL MODEL
# -------------------------
class Principal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# -------------------------
# DEPARTMENT MODEL
# -------------------------
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


# -------------------------
# HOD MODEL
# -------------------------
class HOD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))

    department = db.relationship("Department", backref="hods", lazy=True)
    availabilities = db.relationship("HODAvailability", backref="hod", lazy=True)


# -------------------------
# STAFF MODEL
# -------------------------
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))


# -------------------------
# HOD AVAILABILITY MODEL
# -------------------------
class HODAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hod_id = db.Column(db.Integer, db.ForeignKey("hod.id"))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


# -------------------------
# MEETING MODEL (FIXED)
# -------------------------
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)
    hod_id = db.Column(db.Integer, db.ForeignKey("hod.id"), nullable=True)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    agenda = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Requested")

    staff = db.relationship("Staff", backref="meetings", lazy=True)
    hod = db.relationship("HOD", backref="meetings", lazy=True)


# -------------------------
# REVIEW MODEL
# -------------------------
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meeting.id"))
    summary = db.Column(db.Text)
    improvements = db.Column(db.Text)
    suggestions = db.Column(db.Text)


# -------------------------
# BLOCKLIST MODEL
# -------------------------
class Blocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))   # "hod" or "staff"
    ref_id = db.Column(db.Integer)    # holds hod_id or staff_id
    reason = db.Column(db.String(200))
