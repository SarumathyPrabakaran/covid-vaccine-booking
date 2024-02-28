# covid-vaccine-booking

This is a Flask web application for managing vaccine centers, bookings, and dosage details.

## Features

- User registration and login
- Admin login
- Listing vaccine centers
- Adding, removing vaccine centers (Admin only)
- Booking vaccine slots
- Viewing dosage details
- Logging out

## Requirements

- Python 3.x
- Flask
- Flask-SQLAlchemy

## Installation

1. Clone the repository:

   ```git clone https://github.com/yourusername/vaccine-booking-system.git```

   ```cd vaccine-booking-system```

2. Install dependencies:

    ```pip install -r requirements.txt```

3. Start the flask app:

   By default, this application uses SQLite. If you want to use a different database, modify the SQLALCHEMY_DATABASE_URI in app.py.

    ```python3 app.py```
