
from flask import Flask, render_template, request
import time

app = Flask(__name__)

user_db = {}

parking_lot = {
    f"A{i}": {
        "Status": "Available",
        "User-Assigned": "",
        "Starttime": None
    }
    for i in range(1, 21)
}

current_user = None

# FEE CALCULATION

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
        parking_lot=parking_lot,
        current_user=current_user
    )

# MODULE: VEHICLE REGISTRATION / LOGIN

@app.route("/login", methods=["POST"])
def login():
    global current_user

    license_plate = request.form["license_plate"].strip().upper()

    if not license_plate:
        return "Please enter a license plate."

    user_db[license_plate] = {
        "license_plate": license_plate,
        "fees": user_db.get(license_plate, {}).get("fees", 0.0)
    }

    current_user = license_plate

    return render_template(
        "index.html",
        parking_lot=parking_lot,
        current_user=current_user,
        message=f"Welcome {current_user}!"
    )



# MODULE: SLOT SELECTION & CHECK-IN  (also  TIME TRACKING starts here)

@app.route("/check-in", methods=["POST"])
def check_in():
    global current_user

    if current_user is None:
        return "Please login first."

    # car is already parked
    for spot, info in parking_lot.items():
        if info["User-Assigned"] == current_user:
            return f"{current_user} is already parked at {spot}."

    # The user picks the spot themselves 
    chosen_spot = request.form.get("spot")

    if not chosen_spot or chosen_spot not in parking_lot:
        return "Please select a valid parking spot."

    info = parking_lot[chosen_spot]

    if info["Status"] != "Available":
        return f"Spot {chosen_spot} is no longer available. Please pick another."

    info["Status"] = "Occupied"
    info["User-Assigned"] = current_user
    info["Starttime"] = time.time()  # MODULE 4: arrival time recorded

    return render_template(
        "index.html",
        parking_lot=parking_lot,
        current_user=current_user,
        message=f"{current_user} checked in at spot {chosen_spot}."
    )


# MODULE: PAYMENT

@app.route("/calculate-fee", methods=["POST"])
def calculate_parking_fee():
    global current_user

    if current_user is None:
        return "Please login first."

    for spot, info in parking_lot.items():
        if info["User-Assigned"] == current_user:

            elapsed_seconds = time.time() - info["Starttime"]
            elapsed_hours = elapsed_seconds / 3600

            fee = calculate_fee(elapsed_hours)

            return render_template(
                "payment.html",
                vehicle=current_user,
                spot=spot,
                time_parked=elapsed_hours,
                fee=fee
            )

    return f"{current_user} is not currently parked."


# MODULE: CHECK-OUT & BARRIER CONTROL

@app.route("/check-out", methods=["POST"])
def check_out():
    global current_user

    if current_user is None:
        return "Please login first."

    for spot, info in parking_lot.items():
        if info["User-Assigned"] == current_user:

            elapsed_seconds = time.time() - info["Starttime"]
            elapsed_hours = elapsed_seconds / 3600

            fee = calculate_fee(elapsed_hours)

            payment_text = request.form.get("payment", "0")

            try:
                payment = float(payment_text)
            except ValueError:
                return "Please enter a valid payment amount."

            if payment != fee:
                return render_template(
                    "payment.html",
                    vehicle=current_user,
                    spot=spot,
                    time_parked=elapsed_hours,
                    fee=fee,
                    message=f"Please pay the exact amount of KSh {fee:.2f}."
                )

            # transaction confirmed -> record it
            user_db[current_user]["fees"] += fee
            vehicle = current_user

            # free up the slot (this is the "increase slots by one" step)
            info["Status"] = "Available"
            info["User-Assigned"] = ""
            info["Starttime"] = None

            return render_template(
                "index.html",
                parking_lot=parking_lot,
                current_user=current_user,
                message=(
                    f"Payment successful. "
                    f"{vehicle} checked out of spot {spot}. "
                    f"Amount paid: KSh {fee:.2f}. "
                    f"Barrier opened."
                )
            )

    return f"{current_user} is not currently parked."


@app.route("/logout", methods=["POST"])
def logout():
    global current_user

    if current_user is None:
        return "No vehicle is currently logged in."

    message = f"{current_user} logged out successfully."
    current_user = None

    return render_template(
        "index.html",
        parking_lot=parking_lot,
        current_user=current_user,
        message=message
    )


# MODULE: ADMIN REPORTING

@app.route("/admin")
def admin():
    total_spots = len(parking_lot)
    occupied = sum(1 for info in parking_lot.values() if info["Status"] == "Occupied")
    available = total_spots - occupied
    total_revenue = sum(u["fees"] for u in user_db.values())

    return render_template(
        "admin.html",
        total_spots=total_spots,
        occupied=occupied,
        available=available,
        total_revenue=total_revenue,
        user_db=user_db
    )


if __name__ == "__main__":
    app.run(debug=True)



    

    


