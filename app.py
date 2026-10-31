
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "hospital_management_demo_key"

DATABASE = Path(__file__).with_name("hospital.db")


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables automatically
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home dashboard
@app.route("/")
def index():
    conn = get_db_connection()

    patients = conn.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    doctors = conn.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    appointments = conn.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        patients=patients,
        doctors=doctors,
        appointments=appointments
    )


# Patient registration
@app.route("/patients", methods=["GET", "POST"])
def patients_page():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_text = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            age = int(age_text)
        except ValueError:
            age = 0

        if not name or not gender or not phone or not (1 <= age <= 120):
            conn.close()
            flash("Please enter valid patient details.", "error")
            return redirect(url_for("patients_page"))

        conn.execute(
            "INSERT INTO patients (name, age, gender, phone) VALUES (?, ?, ?, ?)",
            (name, age, gender, phone)
        )

        conn.commit()
        conn.close()

        flash("Patient registered successfully!", "success")
        return redirect(url_for("patients_page"))

    patient_list = conn.execute(
        "SELECT * FROM patients ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("patients.html", patients=patient_list)


# Doctor management
@app.route("/doctors", methods=["GET", "POST"])
def doctors_page():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name or not specialization or not phone:
            conn.close()
            flash("Please fill in all doctor details.", "error")
            return redirect(url_for("doctors_page"))

        conn.execute(
            "INSERT INTO doctors (name, specialization, phone) VALUES (?, ?, ?)",
            (name, specialization, phone)
        )

        conn.commit()
        conn.close()

        flash("Doctor added successfully!", "success")
        return redirect(url_for("doctors_page"))

    doctor_list = conn.execute(
        "SELECT * FROM doctors ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("doctors.html", doctors=doctor_list)


# Appointment booking
@app.route("/appointments", methods=["GET", "POST"])
def appointments_page():
    conn = get_db_connection()

    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        doctor_name = request.form.get("doctor_name", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        reason = request.form.get("reason", "").strip()

        if not all([patient_name, doctor_name, appointment_date, reason]):
            conn.close()
            flash("Please fill in all appointment details.", "error")
            return redirect(url_for("appointments_page"))

        conn.execute(
            """INSERT INTO appointments
               (patient_name, doctor_name, appointment_date, reason)
               VALUES (?, ?, ?, ?)""",
            (patient_name, doctor_name, appointment_date, reason)
        )

        conn.commit()
        conn.close()

        flash("Appointment booked successfully!", "success")
        return redirect(url_for("appointments_page"))

    patient_list = conn.execute(
        "SELECT name FROM patients ORDER BY name"
    ).fetchall()

    doctor_list = conn.execute(
        "SELECT name FROM doctors ORDER BY name"
    ).fetchall()

    appointment_list = conn.execute(
        "SELECT * FROM appointments ORDER BY appointment_date DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "appointments.html",
        patients=patient_list,
        doctors=doctor_list,
        appointments=appointment_list
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
