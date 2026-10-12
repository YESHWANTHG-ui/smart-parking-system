from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

app = Flask(__name__)
app.secret_key = "campus-parking-secret-key"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "campus_parking"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "POSTGRES123")
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def query(sql, params=(), fetch=True):
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            result = cur.fetchall() if fetch else None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@app.route("/")
def dashboard():
    try:
        stats = query("""
            SELECT
              (SELECT COUNT(*) FROM parking_slots) AS total_slots,
              (SELECT COUNT(*) FROM parking_slots WHERE status='Available') AS available_slots,
              (SELECT COUNT(*) FROM parking_slots WHERE status='Occupied') AS occupied_slots,
              (SELECT COUNT(*) FROM vehicles) AS vehicles,
              (SELECT COUNT(*) FROM parking_records WHERE status='Parked') AS currently_parked,
              (SELECT COUNT(*) FROM parking_records WHERE entry_time::date=CURRENT_DATE) AS today_entries,
              (SELECT COUNT(*) FROM parking_records WHERE exit_time::date=CURRENT_DATE) AS today_exits,
              COALESCE((SELECT SUM(fee) FROM parking_records WHERE exit_time::date=CURRENT_DATE),0) AS today_revenue
        """)[0]

        slots = query("SELECT * FROM parking_slots ORDER BY slot_number")
        recent = query("""
            SELECT pr.id, v.vehicle_number, v.owner_name, ps.slot_number,
                   pr.entry_time, pr.exit_time, pr.status, pr.fee
            FROM parking_records pr
            JOIN vehicles v ON v.id=pr.vehicle_id
            JOIN parking_slots ps ON ps.id=pr.slot_id
            ORDER BY pr.entry_time DESC
            LIMIT 8
        """)
        return render_template("dashboard.html", stats=stats, slots=slots, recent=recent)
    except Exception as e:
        return render_template("error.html", error=str(e))

@app.route("/vehicles")
def vehicles():
    data = query("SELECT * FROM vehicles ORDER BY id DESC")
    return render_template("vehicles.html", vehicles=data)

@app.post("/vehicles/add")
def add_vehicle():
    vehicle_number = request.form["vehicle_number"].strip().upper()
    owner_name = request.form["owner_name"].strip()
    vehicle_type = request.form["vehicle_type"]
    try:
        query("""
            INSERT INTO vehicles(vehicle_number, owner_name, vehicle_type)
            VALUES (%s,%s,%s)
        """, (vehicle_number, owner_name, vehicle_type), fetch=False)
        flash("Vehicle registered successfully.", "success")
    except Exception as e:
        flash(f"Could not add vehicle: {e}", "danger")
    return redirect(url_for("vehicles"))

@app.post("/vehicles/delete/<int:vehicle_id>")
def delete_vehicle(vehicle_id):
    try:
        active = query("SELECT id FROM parking_records WHERE vehicle_id=%s AND status='Parked'", (vehicle_id,))
        if active:
            flash("Cannot delete a vehicle that is currently parked.", "warning")
        else:
            query("DELETE FROM vehicles WHERE id=%s", (vehicle_id,), fetch=False)
            flash("Vehicle deleted.", "success")
    except Exception as e:
        flash(f"Could not delete vehicle: {e}", "danger")
    return redirect(url_for("vehicles"))

@app.route("/parking")
def parking():
    slots = query("SELECT * FROM parking_slots ORDER BY slot_number")
    vehicles = query("SELECT * FROM vehicles ORDER BY vehicle_number")
    active_records = query("""
        SELECT pr.id, pr.entry_time, v.vehicle_number, v.owner_name, ps.slot_number
        FROM parking_records pr
        JOIN vehicles v ON v.id=pr.vehicle_id
        JOIN parking_slots ps ON ps.id=pr.slot_id
        WHERE pr.status='Parked'
        ORDER BY pr.entry_time DESC
    """)
    return render_template("parking.html", slots=slots, vehicles=vehicles, active_records=active_records)

@app.post("/parking/entry")
def parking_entry():
    vehicle_id = request.form["vehicle_id"]
    slot_id = request.form["slot_id"]
    try:
        existing = query("SELECT id FROM parking_records WHERE vehicle_id=%s AND status='Parked'", (vehicle_id,))
        slot = query("SELECT status FROM parking_slots WHERE id=%s", (slot_id,))
        if existing:
            flash("This vehicle is already parked.", "warning")
        elif not slot or slot[0]["status"] != "Available":
            flash("Selected slot is not available.", "warning")
        else:
            query("""
                INSERT INTO parking_records(vehicle_id, slot_id, entry_time, status)
                VALUES (%s,%s,NOW(),'Parked')
            """, (vehicle_id, slot_id), fetch=False)
            query("UPDATE parking_slots SET status='Occupied' WHERE id=%s", (slot_id,), fetch=False)
            flash("Vehicle entry recorded.", "success")
    except Exception as e:
        flash(f"Could not record entry: {e}", "danger")
    return redirect(url_for("parking"))

@app.post("/parking/exit/<int:record_id>")
def parking_exit(record_id):
    try:
        record = query("""
            SELECT pr.id, pr.slot_id, pr.entry_time
            FROM parking_records pr
            WHERE pr.id=%s AND pr.status='Parked'
        """, (record_id,))
        if not record:
            flash("Parking record not found.", "warning")
        else:
            r = record[0]
            fee = query("""
                SELECT GREATEST(30, CEIL(EXTRACT(EPOCH FROM (NOW()-%s))/3600) * 20) AS fee
            """, (r["entry_time"],))[0]["fee"]
            query("""
                UPDATE parking_records
                SET exit_time=NOW(), fee=%s, status='Completed'
                WHERE id=%s
            """, (fee, record_id), fetch=False)
            query("UPDATE parking_slots SET status='Available' WHERE id=%s", (r["slot_id"],), fetch=False)
            flash(f"Vehicle exited. Parking fee: ₹{fee}", "success")
    except Exception as e:
        flash(f"Could not record exit: {e}", "danger")
    return redirect(url_for("parking"))

@app.route("/records")
def records():
    data = query("""
        SELECT pr.id, v.vehicle_number, v.owner_name, ps.slot_number,
               pr.entry_time, pr.exit_time, pr.fee, pr.status
        FROM parking_records pr
        JOIN vehicles v ON v.id=pr.vehicle_id
        JOIN parking_slots ps ON ps.id=pr.slot_id
        ORDER BY pr.entry_time DESC
    """)
    return render_template("records.html", records=data)

@app.route("/reports")
def reports():
    daily = query("""
        SELECT entry_time::date AS day,
               COUNT(*) AS entries,
               COUNT(*) FILTER (WHERE exit_time IS NOT NULL) AS exits,
               COALESCE(SUM(fee),0) AS revenue
        FROM parking_records
        GROUP BY entry_time::date
        ORDER BY day DESC
        LIMIT 10
    """)
    return render_template("reports.html", daily=daily)

@app.post("/slots/add")
def add_slot():
    slot_number = request.form["slot_number"].strip().upper()
    slot_type = request.form["slot_type"]
    try:
        query("INSERT INTO parking_slots(slot_number, slot_type) VALUES (%s,%s)",
              (slot_number, slot_type), fetch=False)
        flash("Parking slot added.", "success")
    except Exception as e:
        flash(f"Could not add slot: {e}", "danger")
    return redirect(url_for("dashboard"))

@app.post("/slots/delete/<int:slot_id>")
def delete_slot(slot_id):
    try:
        used = query("SELECT id FROM parking_records WHERE slot_id=%s LIMIT 1", (slot_id,))
        if used:
            flash("Cannot delete a slot that has parking history.", "warning")
        else:
            query("DELETE FROM parking_slots WHERE id=%s", (slot_id,), fetch=False)
            flash("Parking slot deleted.", "success")
    except Exception as e:
        flash(f"Could not delete slot: {e}", "danger")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
