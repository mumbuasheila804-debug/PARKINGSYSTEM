# myGARI PARKING SYSTEM

## Description

myGARI Parking System is a web-based smart parking management system developed using Python and Flask. The system automates parking operations by allowing vehicles to log in, view available parking spaces, select a parking slot, record arrival time, calculate parking fees, process payments, and complete checkout.

## Technologies Used

* Python 3
* Flask
* SQLite
* HTML
* CSS
* Jinja2

## Modules

1. Vehicle Registration / Login
2. Parking Slot Management
3. Slot Selection & Check-In
4. Time Tracking / Duration Calculation
5. Fee Calculation
6. Payment & Transaction Processing
7. Check-Out & Barrier Control
8. Admin Dashboard / Reporting

## Parking Fee Structure

| Parking Duration |     Fee |
| ---------------- | ------: |
| Up to 30 minutes |   KSh 0 |
| Up to 2 hours    |  KSh 50 |
| Up to 4 hours    | KSh 100 |
| Up to 6 hours    | KSh 300 |
| Over 6 hours     | KSh 500 |

## Project Structure

```text
PARKINGSYSTEM/
│
├── app.py
├── database.py
├── parking.db
│
├── templates/
│   ├── index.html
│   ├── payment.html
│   └── admin.html
│
└── static/
    └── style.css
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mumbuasheila804-debug/PARKINGSYSTEM.git
```

### 2. Open the Project Folder

```bash
cd PARKINGSYSTEM
```

### 3. Install Flask

```bash
pip install flask
```

## Running the System

Run the Flask application using:

```bash
python app.py
```

The application will start on:

```text
http://127.0.0.1:5000/
```

Open the address in a web browser to access the parking system.
