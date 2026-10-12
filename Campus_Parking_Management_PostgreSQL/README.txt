CAMPUS PARKING MANAGEMENT SYSTEM
Python Flask + PostgreSQL + pgAdmin

1. REQUIREMENTS
- Python 3.x
- PostgreSQL
- pgAdmin
- VS Code (recommended)

2. CREATE DATABASE
Open pgAdmin:
Servers -> PostgreSQL -> Databases
Right click Databases -> Create -> Database
Database name: campus_parking

3. IMPORT TABLES AND SAMPLE DATA
Open the Query Tool for campus_parking.
Open and run:
database/campus_parking.sql

This creates:
- parking_slots
- vehicles
- parking_records

It also inserts sample data so the dashboard is populated.

4. SET YOUR POSTGRESQL PASSWORD
Copy:
.env.example
to:
.env

Then edit:
DB_PASSWORD=YOUR_REAL_POSTGRES_PASSWORD

Example:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campus_parking
DB_USER=postgres
DB_PASSWORD=your_password

5. INSTALL PYTHON PACKAGES
Open Command Prompt/VS Code terminal in this project folder:

python -m pip install -r requirements.txt

6. START THE PROJECT
python app.py

7. OPEN IN BROWSER
http://127.0.0.1:5000/

8. DASHBOARD FEATURES
- Total slots
- Available slots
- Occupied slots
- Registered vehicles
- Currently parked
- Today's entries
- Today's exits
- Today's revenue
- Live parking slot grid
- Recent parking activity

9. OPERATIONS
Vehicles:
- Register vehicle
- Delete vehicle

Parking:
- Record vehicle entry
- Select an available slot
- Record vehicle exit
- Parking fee is calculated automatically

Reports:
- Daily entries
- Daily exits
- Revenue

IMPORTANT:
Do NOT put your real PostgreSQL password into a public GitHub repository.
