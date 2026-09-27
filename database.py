
import sqlite3


DATABASE = "parking.db"


# MODULE: DATABASE CONNECTION
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# MODULE: DATABASE INITIALIZATION
def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    # Store registered vehicles/users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            license_plate TEXT PRIMARY KEY
        )
    """)

    # Store parking spaces and active parking sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_spaces (
            spot_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'Available',
            license_plate TEXT,
            start_time REAL
        )
    """)

    # Store completed parking transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT NOT NULL,
            spot_id TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            fee REAL NOT NULL
        )
    """)

    # Create 20 parking spaces
    for i in range(1, 21):
        spot_id = f"A{i}"

        cursor.execute("""
            INSERT OR IGNORE INTO parking_spaces
            (spot_id, status, license_plate, start_time)
            VALUES (?, 'Available', NULL, NULL)
        """, (spot_id,))

    connection.commit()
    connection.close()


# MODULE: USER REGISTRATION
def create_user_if_missing(license_plate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (license_plate)
        VALUES (?)
    """, (license_plate,))

    connection.commit()
    connection.close()


# MODULE: PARKING SLOT DISPLAY
def get_parking_lot():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT spot_id, status, license_plate, start_time
        FROM parking_spaces
        ORDER BY spot_id
    """)

    rows = cursor.fetchall()
    connection.close()

    parking_lot = {}

    for row in rows:
        parking_lot[row["spot_id"]] = {
            "spot_id": row["spot_id"],
            "status": row["status"],
            "User-Assigned": row["license_plate"],
            "Starttime": row["start_time"]
        }

    return parking_lot


# MODULE: GET ONE PARKING SPOT
def get_spot(spot_id):
    if not spot_id:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT spot_id, status, license_plate, start_time
        FROM parking_spaces
        WHERE spot_id = ?
    """, (spot_id,))

    row = cursor.fetchone()
    connection.close()

    return row


# MODULE: FIND A USER'S CURRENT PARKING SPOT
def find_spot_for_user(license_plate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT spot_id, status, license_plate, start_time
        FROM parking_spaces
        WHERE license_plate = ?
        AND status = 'Occupied'
    """, (license_plate,))

    row = cursor.fetchone()
    connection.close()

    return row


# MODULE: CHECK-IN / ARRIVAL RECORDING
def check_in_spot(spot_id, license_plate, start_time):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE parking_spaces
        SET status = 'Occupied',
            license_plate = ?,
            start_time = ?
        WHERE spot_id = ?
        AND status = 'Available'
    """, (license_plate, start_time, spot_id))

    connection.commit()
    connection.close()


# MODULE: CHECK-OUT / TRANSACTION RECORDING
def complete_checkout(license_plate, spot_id, fee, end_time):
    connection = get_connection()
    cursor = connection.cursor()

    # Get the original arrival time
    cursor.execute("""
        SELECT start_time
        FROM parking_spaces
        WHERE spot_id = ?
        AND license_plate = ?
    """, (spot_id, license_plate))

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return False

    start_time = row["start_time"]

    # Save completed transaction
    cursor.execute("""
        INSERT INTO parking_history
        (license_plate, spot_id, start_time, end_time, fee)
        VALUES (?, ?, ?, ?, ?)
    """, (
        license_plate,
        spot_id,
        start_time,
        end_time,
        fee
    ))

    # Free the parking space
    cursor.execute("""
        UPDATE parking_spaces
        SET status = 'Available',
            license_plate = NULL,
            start_time = NULL
        WHERE spot_id = ?
    """, (spot_id,))

    connection.commit()
    connection.close()

    return True


# MODULE: ADMIN REPORTING
def get_admin_stats():
    connection = get_connection()
    cursor = connection.cursor()

    # Total parking spaces
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM parking_spaces
    """)
    total_spots = cursor.fetchone()["total"]

    # Occupied spaces
    cursor.execute("""
        SELECT COUNT(*) AS occupied
        FROM parking_spaces
        WHERE status = 'Occupied'
    """)
    occupied = cursor.fetchone()["occupied"]

    # Available spaces
    available = total_spots - occupied

    # Total revenue
    cursor.execute("""
        SELECT COALESCE(SUM(fee), 0) AS revenue
        FROM parking_history
    """)
    total_revenue = cursor.fetchone()["revenue"]

    connection.close()

    return {
        "total_spots": total_spots,
        "occupied": occupied,
        "available": available,
        "total_revenue": total_revenue
    }


# MODULE: USER REPORTING
def get_user_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT license_plate
        FROM users
        ORDER BY license_plate
    """)

    rows = cursor.fetchall()
    connection.close()

    user_db = {}

    for row in rows:
        user_db[row["license_plate"]] = {
            "license_plate": row["license_plate"]
        }

    return user_db


# Initialize the database
init_db()



