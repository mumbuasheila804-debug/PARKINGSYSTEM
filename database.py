
import sqlite3
from datetime import datetime

DATABASE = "parking.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Users who are currently logged in
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            login_time TEXT NOT NULL
        )
    """)

    # Parking spaces
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_spaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            space_number TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available',
            username TEXT,
            start_time TEXT
        )
    """)

    # Parking history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            space_number TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            amount_paid INTEGER NOT NULL
        )
    """)

    # Create 20 parking spaces: A1 - A20
    for i in range(1, 21):
        space_number = f"A{i}"

        cursor.execute("""
            INSERT OR IGNORE INTO parking_spaces
            (space_number, status)
            VALUES (?, 'Available')
        """, (space_number,))

    connection.commit()
    connection.close()


def add_user(username):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO users (username, login_time)
            VALUES (?, ?)
        """, (username, login_time))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def remove_user(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE username = ?
    """, (username,))

    connection.commit()
    connection.close()


def user_exists(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    return user is not None


def get_available_spaces():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM parking_spaces
        WHERE status = 'Available'
        ORDER BY id
    """)

    spaces = cursor.fetchall()

    connection.close()

    return spaces


def get_all_spaces():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM parking_spaces
        ORDER BY id
    """)

    spaces = cursor.fetchall()

    connection.close()

    return spaces


def assign_space(username, space_number):
    connection = get_connection()
    cursor = connection.cursor()

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE parking_spaces
        SET status = 'Occupied',
            username = ?,
            start_time = ?
        WHERE space_number = ?
        AND status = 'Available'
    """, (username, start_time, space_number))

    connection.commit()

    success = cursor.rowcount > 0

    connection.close()

    return success


def get_user_space(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM parking_spaces
        WHERE username = ?
        AND status = 'Occupied'
    """, (username,))

    space = cursor.fetchone()

    connection.close()

    return space


def calculate_fee(duration_minutes):
    if duration_minutes <= 30:
        return 0

    elif duration_minutes <= 120:
        return 50

    elif duration_minutes <= 240:
        return 100

    elif duration_minutes <= 360:
        return 300

    else:
        return 500


def checkout_user(username):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM parking_spaces
        WHERE username = ?
        AND status = 'Occupied'
    """, (username,))

    space = cursor.fetchone()

    if space is None:
        connection.close()
        return None

    start_time = datetime.strptime(
        space["start_time"],
        "%Y-%m-%d %H:%M:%S"
    )

    end_time = datetime.now()

    duration = end_time - start_time
    duration_minutes = int(duration.total_seconds() / 60)

    amount_paid = calculate_fee(duration_minutes)

    # Save the completed parking session
    cursor.execute("""
        INSERT INTO parking_history
        (
            username,
            space_number,
            start_time,
            end_time,
            duration_minutes,
            amount_paid
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        space["space_number"],
        space["start_time"],
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
        duration_minutes,
        amount_paid
    ))

    # Make the parking space available again
    cursor.execute("""
        UPDATE parking_spaces
        SET status = 'Available',
            username = NULL,
            start_time = NULL
        WHERE space_number = ?
    """, (space["space_number"],))

    connection.commit()
    connection.close()

    return {
        "space_number": space["space_number"],
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": duration_minutes,
        "amount_paid": amount_paid
    }


def get_parking_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM parking_history
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    connection.close()

    return history


# Create the database automatically when this file is loaded
create_database()

