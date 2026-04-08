import os
import os

from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import re

app = Flask(__name__)

# ── Data Storage (in-memory) ──
patients = {}
doctors = {
    "999": {"name": "Saif", "specialty": "Orthopedic"},
    "888": {"name": "Ziad", "specialty": "Dentistry"},
    "777": {"name": "Nour", "specialty": "Ophthalmology"},
    "666": {"name": "Omar", "specialty": "Surgeon"},
    "555": {"name": "Rodi", "specialty": "Internist"},
}
current_doctor = None
ADMIN_PASSWORD = "clinic2024"
app.secret_key = "hospital_secret_key"

@app.route("/")
def index():
    return render_template("index.html", doctor=current_doctor)

@app.route("/login", methods=["POST"])
def login():
    global current_doctor
    doctor_id = request.form.get("doctor_id")
    if doctor_id in doctors:
        current_doctor = doctors[doctor_id]
        current_doctor["id"] = doctor_id
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    global current_doctor
    current_doctor = None
    return redirect(url_for("index"))

@app.route("/patients")
def patient_list():
    return render_template("patients.html", patients=patients, doctor=current_doctor)

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        pid = request.form.get("patient_id")
        patients[pid] = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "illness": request.form.get("illness"),
            "note": request.form.get("note", ""),
            "appointments": []
        }
        return redirect(url_for("patient_list"))
    return render_template("add_patient.html", doctor=current_doctor)

@app.route("/patient/<pid>")
def patient_detail(pid):
    patient = patients.get(pid)
    return render_template("patient_detail.html", patient=patient, pid=pid, doctor=current_doctor)

@app.route("/add_note/<pid>", methods=["POST"])
def add_note(pid):
    note = request.form.get("note")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    patients[pid]["note"] += f"\n[{timestamp}] {note}"
    return redirect(url_for("patient_detail", pid=pid))

@app.route("/add_appointment/<pid>", methods=["POST"])
def add_appointment(pid):
    date = request.form.get("appointment_date")
    patients[pid]["appointments"].append(date)
    return redirect(url_for("patient_detail", pid=pid))

@app.route("/remove_patient/<pid>")
def remove_patient(pid):
    patients.pop(pid, None)
    return redirect(url_for("patient_list"))

@app.route("/doctors")
def doctor_list():
    return render_template("doctors.html", doctors=doctors, doctor=current_doctor)

@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    did = request.form.get("doctor_id")
    doctors[did] = {
        "name": request.form.get("name"),
        "specialty": request.form.get("specialty")
    }
    return redirect(url_for("doctor_list"))

@app.route("/remove_doctor/<did>")
def remove_doctor(did):
    doctors.pop(did, None)
    return redirect(url_for("doctor_list"))

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("password") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("index"))
    return render_template("index.html", error="Wrong password", doctor=None)

@app.route("/admin_logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/edit_doctor/<did>", methods=["GET", "POST"])
def edit_doctor(did):
    doctor = doctors.get(did)
    if request.method == "POST":
        doctors[did]["name"] = request.form.get("name")
        doctors[did]["specialty"] = request.form.get("specialty")
        return redirect(url_for("doctor_list"))
    return render_template("edit_doctor.html", did=did, doctor=doctor)

if __name__ == "__main__":
      app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))