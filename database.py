"""SQLite storage for the Campus Transit demo."""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).with_name("campus_transit.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','driver','student')),
            full_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT NOT NULL UNIQUE,
            route_name TEXT NOT NULL,
            driver_user_id INTEGER REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            bus_id INTEGER REFERENCES buses(id)
        );
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_id INTEGER NOT NULL REFERENCES buses(id),
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                [
                    ("admin", "admin123", "admin", "Campus Administrator"),
                    ("driver1", "driver123", "driver", "Demo Driver"),
                    ("student1", "student123", "student", "Demo Student"),
                ],
            )
            driver_id = conn.execute(
                "SELECT id FROM users WHERE username='driver1'"
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO buses(bus_number,route_name,driver_user_id) VALUES(?,?,?)",
                ("CT-01", "Main Gate - Campus", driver_id),
            )
            bus_id = conn.execute("SELECT id FROM buses WHERE bus_number='CT-01'").fetchone()["id"]
            conn.execute(
                "INSERT INTO students(student_code,full_name,bus_id) VALUES(?,?,?)",
                ("STU001", "Demo Student", bus_id),
            )


def authenticate(username, password):
    with connect() as conn:
        return conn.execute(
            "SELECT id, username, role, full_name FROM users WHERE username=? AND password=?",
            (username.strip(), password),
        ).fetchone()


def dashboard_data():
    with connect() as conn:
        return {
            "students": conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "drivers": conn.execute("SELECT COUNT(*) FROM users WHERE role='driver'").fetchone()[0],
            "buses": conn.execute("SELECT COUNT(*) FROM buses").fetchone()[0],
            "bus_rows": conn.execute("""
                SELECT b.bus_number, b.route_name, u.full_name AS driver
                FROM buses b LEFT JOIN users u ON u.id=b.driver_user_id
                ORDER BY b.bus_number
            """).fetchall(),
            "student_rows": conn.execute("""
                SELECT s.student_code, s.full_name, COALESCE(b.bus_number,'Not assigned') AS bus
                FROM students s LEFT JOIN buses b ON b.id=s.bus_id
                ORDER BY s.full_name
            """).fetchall(),
        }


def bus_for_driver(user_id):
    with connect() as conn:
        return conn.execute(
            "SELECT id, bus_number, route_name FROM buses WHERE driver_user_id=?",
            (user_id,),
        ).fetchone()


def bus_for_student(username):
    with connect() as conn:
        return conn.execute("""
            SELECT b.id, b.bus_number, b.route_name
            FROM students s JOIN buses b ON b.id=s.bus_id
            JOIN users u ON u.username=?
            WHERE s.student_code = (SELECT student_code FROM students WHERE full_name=u.full_name LIMIT 1)
            LIMIT 1
        """, (username,)).fetchone()


def latest_locations():
    with connect() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT l.bus_id, b.bus_number, l.latitude, l.longitude, l.updated_at
            FROM locations l JOIN buses b ON b.id=l.bus_id
            WHERE l.id IN (SELECT MAX(id) FROM locations GROUP BY bus_id)
        """).fetchall()]


def save_location(bus_id, latitude, longitude):
    with connect() as conn:
        conn.execute(
            "INSERT INTO locations(bus_id,latitude,longitude) VALUES(?,?,?)",
            (bus_id, latitude, longitude),
        )
