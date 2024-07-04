# Journal App Backend

This backend implementation covers the features listed below:

1. User Authentication: Registration, login, and JWT-based authentication.
2. Journal Entry Management: CRUD operations for journal entries.
3. Categorization: Entries can be categorized.
4. Summary View: Endpoint to fetch summary data for given periods (daily, weekly, monthly).
5. Settings: Users can update their username and password.

## Tech Stack

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- PostgreSQL

## Project Structure

journal_app/
├── app/
│   ├── init.py
│   ├── models.py
│   ├── routes.py
│   └── utils.py
├── config.py
├── requirements.txt
└── run.py

### To set up and run the backend

1. Clone the repository 
    - `https://github.com/bryokn/journal_backend.git`
    - cd journal_backend
2. Create a virtual environment and activate it:
    `source venv/bin/activate`  (Ubuntu)
3. Install the required packages:
    `pip install -r requirements.txt`
4. Set up the PostgreSQL database:
    `CREATE DATABASE journal_app_db;`
    `CREATE USER your_username WITH PASSWORD 'your_password';`
    `GRANT ALL PRIVILEGES ON DATABASE journal_app_db TO your_username;`
    `\q`
5. Update the `config.py` file with your database URI:
    `Copy
6. Update the `config.py` file with your database URI:
    `postgresql://your_username:your_password@localhost/journal_app_db`
7. Run the application:
    `python3 run.py`

This will start the Flask development server, and your backend will be accessible at `http://localhost:5000` or `http://127.0.0.1:5000`.

## API Endpoints

- POST /register - Register a new user
- POST /login - Authenticate a user and receive a token
- GET /entries - Get all journal entries for the authenticated user
- POST /entries - Create a new journal entry
- GET /entries/<entry_id> - Get a specific journal entry
- PUT /entries/<entry_id> - Update a specific journal entry
- DELETE /entries/<entry_id> - Delete a specific journal entry
- GET /summary - Get a summary of journal entries (query parameter: period)
- GET /user - Get user information
- PUT /user - Update user information.

You can test these API endpoints using a tool like Postman.

## Contact

Kipkirui Brian - `kipkiruibn@gmail.com`
