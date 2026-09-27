from flask import Flask, render_template, request
import time

import database as db

app = Flask(__name__)


db.init_db()


current_user = None


# MODULE: FEE CALCULATION
def calculate_fee(time_in_hours):
    if time_in_hours <= 0.5:
        return 0
    elif time_in_hours <= 2:
        return 50
    elif time_in_hours <= 4:
        return 100
    elif time_in_hours <= 6:
        return 300
    else:
        return 500


# MODULE: PARKING SLOT DISPLAY
@app.route("/")
def home():
    return render_template(
        "index.html",
        parking_lot=db.get_parking_lot(),
        current_user=current_user
    )


# MODULE: VEHICLE REGISTRATION / LOGIN
@app.route("/login", methods=["POST"])
def login():
    global current_user

    license_plate = request.form["license_plate"].strip().upper()

    if not license_plate:
        return "Please enter a license plate."

    db.create_user_if_missing(license_plate)
    current_user = license_plate

    return render_template(
        "index.html",
        parking_lot=db.get_parking_lot(),
        current_user=current_user,
        message=f"Welcome {current_user}!"
    )


# MODULE: SLOT SELECTION & CHECK-IN  (+ MODULE: TIME TRACKING starts here)
@app.route("/check-in", methods=["POST"])
def check_in():
    if current_user is None:
        return "Please login first."

    already = db.find_spot_for_user(current_user)
    if already:
        return f"{current_user} is already parked at {already['spot_id']}."

    chosen_spot = request.form.get("spot")
    row = db.get_spot(chosen_spot)

    if row is None:
        return "Please select a valid parking spot."

    if row["status"] != "Available":
        return f"Spot {chosen_spot} is no longer available. Please pick another."

    db.check_in_spot(chosen_spot, current_user, time.time())  # MODULE: arrival time recorded

    return render_template(
        "index.html",
        parking_lot=db.get_parking_lot(),
        current_user=current_user,
        message=f"{current_user} checked in at spot {chosen_spot}."
    )


# MODULE: PAYMENT / TRANSACTION PROCESSING (fee preview before paying)
@app.route("/calculate-fee", methods=["POST"])
def calculate_parking_fee():
    if current_user is None:
        return "Please login first."

    row = db.find_spot_for_user(current_user)
    if row is None:
        return f"{current_user} is not currently parked."

    elapsed_seconds = time.time() - row["start_time"]
    elapsed_hours = elapsed_seconds / 3600
    fee = calculate_fee(elapsed_hours)

    return render_template(
        "payment.html",
        vehicle=current_user,
        spot=row["spot_id"],
        time_parked=elapsed_hours,
        fee=fee
    )


# MODULE: CHECK-OUT & BARRIER CONTROL
@app.route("/check-out", methods=["POST"])
def check_out():
    if current_user is None:
        return "Please login first."

    row = db.find_spot_for_user(current_user)
    if row is None:
        return f"{current_user} is not currently parked."

    spot = row["spot_id"]
    elapsed_seconds = time.time() - row["start_time"]
    elapsed_hours = elapsed_seconds / 3600
    fee = calculate_fee(elapsed_hours)

    payment_text = request.form.get("payment", "0")

    try:
        payment = float(payment_text)
    except ValueError:
        return "Please enter a valid payment amount."

    # Exact-amount check (rounded to cents to avoid float precision issues)
    if round(payment, 2) != round(fee, 2):
        return render_template(
            "payment.html",
            vehicle=current_user,
            spot=spot,
            time_parked=elapsed_hours,
            fee=fee,
            message=f"Please pay the exact amount of KSh {fee:.2f}."
        )

    db.complete_checkout(current_user, spot, fee, time.time())

    return render_template(
        "index.html",
        parking_lot=db.get_parking_lot(),
        current_user=current_user,
        message=(
            f"Payment successful. "
            f"{current_user} checked out of spot {spot}. "
            f"Amount paid: KSh {fee:.2f}. "
            f"Barrier opened."
        )
    )


@app.route("/logout", methods=["POST"])
def logout():
    global current_user

    if current_user is None:
        return "No vehicle is currently logged in."

    message = f"{current_user} logged out successfully."
    current_user = None

    return render_template(
        "index.html",
        parking_lot=db.get_parking_lot(),
        current_user=current_user,
        message=message
    )


# MODULE: ADMIN DASHBOARD / REPORTING
@app.route("/admin")
def admin():
    stats = db.get_admin_stats()

    return render_template(
        "admin.html",
        total_spots=stats["total_spots"],
        occupied=stats["occupied"],
        available=stats["available"],
        total_revenue=stats["total_revenue"],
        user_db=db.get_user_db()
    )


if __name__ == "__main__":
    app.run(debug=True)