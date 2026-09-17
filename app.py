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


@app.route("/")
def home():
    return render_template(
        "index.html",
        parking_lot=parking_lot,
        current_user=current_user
    )


@app.route("/login", methods=["POST"])
def login():
    global current_user

    license_plate = request.form["license_plate"].strip().upper()

    if not license_plate:
        return "Please enter a license plate."

    user_db[license_plate] = {
        "license_plate": license_plate,
        "fees": 0.0
    }

    current_user = license_plate

    return render_template(
        "index.html",
        parking_lot=parking_lot,
        current_user=current_user,
        message=f"Welcome {current_user}!"
    )


@app.route("/check-in", methods=["POST"])
def check_in():
    global current_user

    if current_user is None:
        return "Please login first."

    for spot, info in parking_lot.items():

        if info["User-Assigned"] == current_user:
            return f"{current_user} is already parked at {spot}."

    for spot, info in parking_lot.items():

        if info["Status"] == "Available":

            info["Status"] = "Occupied"
            info["User-Assigned"] = current_user
            info["Starttime"] = time.time()

            return render_template(
                "index.html",
                parking_lot=parking_lot,
                current_user=current_user,
                message=f"{current_user} checked in at spot {spot}."
            )

    return "Parking lot is full. No spots available."


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

            user_db[current_user]["fees"] += fee

            vehicle = current_user

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


if __name__ == "__main__":
    app.run(debug=True)

    


    
    




    

    


