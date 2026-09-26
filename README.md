myGari  PARKING SYSTEM

This is a flask application that implements a smart parking system. A vehicle can login to the application, select an open slot, park and pay an exact fee to exit and open the barrier.
## DESCRIPTION
This application enables users to:

- Login with the vehicle's plate number.
- See a grid of all parking slots with available and occupied slots.
- Choose which slot to park from the available slots.
- Calculates the amount paid based on how long a vehicle is parked.
- Accepts exact amount payment from the user.

- The vehicle leaves and the space is opened for other vehicles.
- The admin gets to know the total number of vehicles and the amount paid.
### LANGUAGES USED
- Python 3
- Flask
- jinja2 for html templates
- Css for styling
- Python dictionaries
### PROJECT STRUCTURE
.
├── app.py
├── templates
│   ├── index.html
│   ├── payment.html
│   └── admin.html
└── static
└── style.css
### MODULES CREATED
| # | Module | Location |
|---|--------|----------|
| 1 | Vehicle registration or login | `/login` |
| 2 | Parking slot | `/` , `parking_lot` dictionary |
| 3 | Slot selection and check in | `/check-in` |
| 4 | Time tracking | Starttime |
| 5 | Fee calculation | `calculate_fee()` |
| 6 | Payment | `/calculate-fee` , `/check-out` |
| 7 | Check-out and barrier control | `/check-out` |
| 8 | Admin dashboard/reporting | `/admin` |
This application uses the following fee schedule:
Duration Fee
up to 30 mins free
up to 2 hours 50
up to 4 hours 100
up to 6 hours 300
over 6 hours 500
## How to Use
### Requirements
- python3.8
- pip
### Installation
To install the application, run the commands below.
```bash
git clone
cd
# (optional) python -m venv venv
# (optional) source venv/bin/activate
pip install flask
```
### Start the App
To start the app, run the command below:
```bash
python app.py
```
Then open your browser and navigate to http://127.0.0.1:5000 .
### Usage
- Sign in with your vehicle plate number and click login to continue.
- Choose an available slot from those you see on the screen and click check in.
- After finishing parking, click calculate parking fee to calculate the amount due.
- The application will prompt you with the time you parked, click pay to continue.
- Make sure to pay the exact amount due and the application will clear you upon exit.
- When you want to view the total number of vehicles and the amount paid go to the admin dashboard .
## Known Limitations
- The vehicle data is stored in a python dictionary and hence deleted on restarting the server.
- Only one vehicle can be logged in at a time.
- This application does not support multiple simultaneous users.
- Only one user is allowed at a time.
- The admin dashboard has no log in authentication.

## License

This project was developement for an assignment.
