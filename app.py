from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date
from models import (
    db, Principal, HOD, Staff, Department,
    HODAvailability, Meeting, Review, Blocklist
)

app = Flask(__name__)
app.config.update(
    SECRET_KEY="svit_secret_key",
    SQLALCHEMY_DATABASE_URI="sqlite:///csms.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)

# ----------------------------------------------------
# INITIAL DB SETUP
# ----------------------------------------------------
with app.app_context():
    db.create_all()

    # Create default principal
    if not Principal.query.first():
        admin = Principal(
            name="Principal",
            email="principal@csms.com",
            password="admin123"
        )
        db.session.add(admin)
        db.session.commit()

    # Insert Departments
    if Department.query.count() == 0:
        for dept in ["Computer Science", "Mechanical", "Civil", "Electronics", "Management"]:
            db.session.add(Department(name=dept))
        db.session.commit()


# ----------------------------------------------------
# HOME + LOGOUT
# ----------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/")


# ----------------------------------------------------
# LOGIN ROUTES
# ----------------------------------------------------
@app.route("/login/principal", methods=["GET", "POST"])
def login_principal():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        u = Principal.query.filter_by(email=email).first()
        if not u or u.password != password:
            flash("Invalid credentials!", "danger")
            return redirect("/login/principal")

        session["role"] = "principal"
        session["id"] = u.id
        session["name"] = u.name
        return redirect("/dashboard/principal")

    return render_template("login_principal.html")


@app.route("/login/hod", methods=["GET", "POST"])
def login_hod():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Fetch HOD
        u = HOD.query.filter_by(email=email).first()

        # Invalid login
        if not u or u.password != password:
            flash("Invalid HOD credentials!", "danger")
            return redirect("/login/hod")

        # Check if blacklisted
        black = Blocklist.query.filter_by(role="hod", ref_id=u.id).first()
        if black:
            flash("You are BLACKLISTED by Principal!", "danger")
            return redirect("/login/hod")

        # Success → Save session
        session["role"] = "hod"
        session["id"] = u.id
        session["name"] = u.name

        return redirect("/dashboard/hod")

    return render_template("login_hod.html")


@app.route("/login/staff", methods=["GET", "POST"])
def login_staff():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        u = Staff.query.filter_by(email=email).first()

        if not u or u.password != password:
            flash("Invalid Staff credentials!", "danger")
            return redirect("/login/staff")

        # Check blacklist
        if Blocklist.query.filter_by(role="staff", ref_id=u.id).first():
            flash("You are BLACKLISTED. Contact Principal.", "danger")
            return redirect("/login/staff")

        session["role"] = "staff"
        session["id"] = u.id
        session["name"] = u.name
        return redirect("/dashboard/staff")

    return render_template("login_staff.html")


# ----------------------------------------------------
# REGISTRATION ROUTES (PUBLIC)
# ----------------------------------------------------
@app.route("/register/hod", methods=["GET", "POST"])
def register_hod_public():
    if session.get("role"):
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email")

        if HOD.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect("/register/hod")

        new_hod = HOD(
            name=request.form.get("name"),
            email=email,
            password=request.form.get("password"),
            phone=request.form.get("phone"),
            department_id=request.form.get("department_id")
        )
        db.session.add(new_hod)
        db.session.commit()

        flash("HOD registered successfully!", "success")
        return redirect("/login/hod")

    return render_template("register_hod.html", departments=Department.query.all())


@app.route("/register/staff", methods=["GET", "POST"])
def register_staff_public():
    if session.get("role"):
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email")

        if Staff.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect("/register/staff")

        new_staff = Staff(
            name=request.form.get("name"),
            email=email,
            password=request.form.get("password"),
            gender=request.form.get("gender"),
            phone=request.form.get("phone"),
            address=request.form.get("address")
        )
        db.session.add(new_staff)
        db.session.commit()

        flash("Staff registered successfully!", "success")
        return redirect("/login/staff")

    return render_template("register_staff.html")


# ----------------------------------------------------
# PRINCIPAL DASHBOARD
# ----------------------------------------------------
@app.route("/dashboard/principal")
def dashboard_principal():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    return render_template(
        "principal_dashboard.html",
        hod_count=HOD.query.count(),
        staff_count=Staff.query.count(),
        meeting_count=Meeting.query.count(),
        blacklist_count=Blocklist.query.count(),
        meetings=Meeting.query.order_by(Meeting.date.desc()).limit(10).all()
    )


# ----------------------------------------------------
# PRINCIPAL — MANAGE HODS
# ----------------------------------------------------
@app.route("/principal/hods")
def principal_hods():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    return render_template("principal_hods.html", hods=HOD.query.all())


@app.route("/principal/hods/add", methods=["GET", "POST"])
def principal_add_hod():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    if request.method == "POST":
        new_hod = HOD(
            name=request.form.get("name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            password=request.form.get("password"),
            department_id=request.form.get("department_id")
        )
        db.session.add(new_hod)
        db.session.commit()

        flash("New HOD added!", "success")
        return redirect("/principal/hods")

    return render_template("principal_add_hod.html", departments=Department.query.all())


# ----------------------------------------------------
# PRINCIPAL — MANAGE STAFF
# ----------------------------------------------------
@app.route("/principal/staff")
def principal_staff():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    return render_template("principal_staff.html", staff=Staff.query.all())


@app.route("/principal/staff/add", methods=["GET", "POST"])
def principal_add_staff():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    if request.method == "POST":
        new_staff = Staff(
            name=request.form.get("name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            password=request.form.get("password")
        )
        db.session.add(new_staff)
        db.session.commit()

        flash("New staff added!", "success")
        return redirect("/principal/staff")

    return render_template("principal_add_staff.html")


# ----------------------------------------------------
# PRINCIPAL — BLACKLIST HOD
# ----------------------------------------------------
@app.route("/principal/hods/blacklist/<int:hod_id>")
def principal_blacklist_hod(hod_id):
    if session.get("role") != "principal":
        return redirect("/login/principal")

    hod = HOD.query.get_or_404(hod_id)

    if Blocklist.query.filter_by(role="hod", ref_id=hod.id).first():
        flash("HOD already blacklisted.", "warning")
        return redirect("/principal/hods")

    bl = Blocklist(role="hod", ref_id=hod.id, reason="Misconduct")
    db.session.add(bl)
    db.session.commit()

    flash(f"HOD '{hod.name}' blacklisted!", "danger")
    return redirect("/principal/hods")


# ----------------------------------------------------
# PRINCIPAL — BLACKLIST STAFF
# ----------------------------------------------------
@app.route("/principal/staff/blacklist/<int:staff_id>")
def principal_blacklist_staff(staff_id):
    if session.get("role") != "principal":
        return redirect("/login/principal")

    st = Staff.query.get_or_404(staff_id)

    if Blocklist.query.filter_by(role="staff", ref_id=st.id).first():
        flash("Staff already blacklisted.", "warning")
        return redirect("/principal/staff")

    bl = Blocklist(role="staff", ref_id=st.id, reason="Misconduct")
    db.session.add(bl)
    db.session.commit()

    flash(f"Staff '{st.name}' blacklisted!", "danger")
    return redirect("/principal/staff")


# ----------------------------------------------------
# PRINCIPAL — VIEW BLACKLIST
# ----------------------------------------------------
@app.route("/principal/blacklist")
def principal_blacklist():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    entries = Blocklist.query.all()
    view_rows = []

    for e in entries:
        name = "Unknown"

        if e.role == "hod":
            hod = HOD.query.get(e.ref_id)
            name = hod.name if hod else f"HOD (ID {e.ref_id})"

        elif e.role == "staff":
            st = Staff.query.get(e.ref_id)
            name = st.name if st else f"Staff (ID {e.ref_id})"

        view_rows.append({
            "id": e.id,
            "name": name,
            "role": e.role,
            "reason": e.reason
        })

    return render_template("principal_blacklist.html", bl=view_rows)


# ----------------------------------------------------
# HOD DASHBOARD
# ----------------------------------------------------
@app.route("/dashboard/hod")
def dashboard_hod():
    if session.get("role") != "hod":
        return redirect("/login/hod")

    hod = HOD.query.get(session["id"])
    today = date.today()

    return render_template(
        "hod_dashboard.html",
        today_meetings=Meeting.query.filter_by(hod_id=hod.id, date=today).count(),
        upcoming_meetings=Meeting.query.filter(Meeting.hod_id == hod.id, Meeting.date > today).count(),
        completed_meetings=Meeting.query.filter_by(hod_id=hod.id, status="Completed").count(),
        availability=hod.availabilities,
        meetings=Meeting.query.filter_by(hod_id=hod.id).order_by(Meeting.date).all()
    )


# ----------------------------------------------------
# HOD — ADD AVAILABILITY
# ----------------------------------------------------
@app.route("/hod/availability/add", methods=["GET", "POST"])
def add_availability():
    if session.get("role") != "hod":
        return redirect("/login/hod")

    if request.method == "POST":
        a = HODAvailability(
            hod_id=session["id"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            start_time=datetime.strptime(request.form["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(request.form["end_time"], "%H:%M").time()
        )
        db.session.add(a)
        db.session.commit()

        flash("Availability added.", "success")
        return redirect("/dashboard/hod")

    return render_template("hod_add_availability.html")


# ----------------------------------------------------
# STAFF DASHBOARD
# ----------------------------------------------------
@app.route("/dashboard/staff")
def dashboard_staff():
    if session.get("role") != "staff":
        return redirect("/login/staff")

    st = Staff.query.get(session["id"])

    return render_template(
        "staff_dashboard.html",
        meetings=Meeting.query.filter_by(staff_id=st.id).all(),
        total=Meeting.query.filter_by(staff_id=st.id).count(),
        upcoming=Meeting.query.filter(Meeting.staff_id == st.id, Meeting.date >= date.today()).count(),
        completed=Meeting.query.filter_by(staff_id=st.id, status="Completed").count()
    )


# ----------------------------------------------------
# STAFF — REQUEST MEETING
# ----------------------------------------------------
@app.route("/meeting/request", methods=["GET", "POST"])
def request_meeting():
    if session.get("role") != "staff":
        return redirect("/login/staff")

    if request.method == "POST":
        m = Meeting(
            staff_id=session["id"],
            hod_id=request.form["hod_id"],
            date=datetime.strptime(request.form["date"], "%Y-%m-%d").date(),
            time=datetime.strptime(request.form["time"], "%H:%M").time(),
            agenda=request.form["agenda"],
            status="Requested"
        )
        db.session.add(m)
        db.session.commit()

        flash("Meeting requested!", "success")
        return redirect("/dashboard/staff")

    return render_template("staff_request_meeting.html", hods=HOD.query.all())


# ----------------------------------------------------
# HOD — ADD REVIEW
# ----------------------------------------------------
@app.route("/meeting/<int:id>/review", methods=["GET", "POST"])
def review_meeting(id):
    if session.get("role") != "hod":
        return redirect("/login/hod")

    m = Meeting.query.get_or_404(id)

    if request.method == "POST":
        r = Review(
            meeting_id=id,
            summary=request.form["summary"],
            improvements=request.form["improvements"],
            suggestions=request.form["suggestions"]
        )
        db.session.add(r)
        m.status = "Completed"
        db.session.commit()

        flash("Review submitted!", "success")
        return redirect("/dashboard/hod")

    return render_template("hod_add_review.html", meeting=m)


# ----------------------------------------------------
# PRINCIPAL — SELECTIVE & BULK MEETING SCHEDULER (ONLY COPY LEFT)
# ----------------------------------------------------
@app.route("/principal/meeting/bulk", methods=["GET", "POST"])
def principal_bulk_meeting_fixed():
    if session.get("role") != "principal":
        return redirect("/login/principal")

    all_staff = Staff.query.all()
    all_hods = HOD.query.all()

    if request.method == "POST":
        mode = request.form.get("mode")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        agenda = request.form.get("agenda")

        if not date_str or not time_str:
            flash("Please select date and time.", "danger")
            return redirect("/principal/meeting/bulk")

        date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_val = datetime.strptime(time_str, "%H:%M").time()

        selected_staff = []
        selected_hods = []

        if mode == "all_staff":
            selected_staff = all_staff

        elif mode == "all_hod":
            selected_hods = all_hods

        elif mode == "all_both":
            selected_staff = all_staff
            selected_hods = all_hods

        elif mode == "selected":
            staff_ids = request.form.getlist("staff_ids")
            hod_ids = request.form.getlist("hod_ids")

            if staff_ids:
                selected_staff = Staff.query.filter(Staff.id.in_(staff_ids)).all()
            if hod_ids:
                selected_hods = HOD.query.filter(HOD.id.in_(hod_ids)).all()

        created = 0

        for st in selected_staff:
            m = Meeting(
                staff_id=st.id,
                hod_id=None,
                date=date_val,
                time=time_val,
                agenda=agenda,
                status="Scheduled"
            )
            db.session.add(m)
            created += 1

        for hd in selected_hods:
            m = Meeting(
                staff_id=None,
                hod_id=hd.id,
                date=date_val,
                time=time_val,
                agenda=agenda,
                status="Scheduled"
            )
            db.session.add(m)
            created += 1

        if created == 0:
            flash("No users selected.", "warning")
        else:
            db.session.commit()
            flash(f"Meetings scheduled for {created} users!", "success")

        return redirect("/dashboard/principal")

    return render_template(
        "principal_bulk_meeting.html",
        staff_list=all_staff,
        hod_list=all_hods
    )


# ----------------------------------------------------
# ERROR HANDLERS
# ----------------------------------------------------
@app.errorhandler(404)
def error_404(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error_500(e):
    return render_template("500.html"), 500


# ----------------------------------------------------
# RUN SERVER
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
