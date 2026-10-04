# Employee Leave Management API

A RESTful Employee Leave Management API built with FastAPI for managing employee leave requests.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Authentication
- Argon2 Password Hashing

## Features

- User registration and login
- Secure password hashing
- JWT authentication
- Protected user profile
- Create, view, update, and delete leave requests
- User-based authorization
- Leave date validation
- Supporting document uploads
- PDF, JPG, JPEG, and PNG file validation

## Project Structure

```fastapi-learning/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── security.py
├── requirements.txt
├── leave_management.db
├── uploads/
└── .gitignore
```
## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd fastapi-learning
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## API Documentation

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Main Endpoints

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| POST   | `/register`             | Register a user              |
| POST   | `/login`                | Login and get JWT            |
| GET    | `/profile`              | Get user profile             |
| POST   | `/leaves`               | Create a leave request       |
| GET    | `/leaves`               | Get user's leaves            |
| GET    | `/leaves/{id}`          | Get a specific leave         |
| PATCH  | `/leaves/{id}`          | Update a leave               |
| DELETE | `/leaves/{id}`          | Delete a leave               |
| POST   | `/leaves/{id}/document` | Upload a supporting document |

## Authentication

Protected endpoints require a JWT Bearer token:

```text
Authorization: Bearer <your-token>
```

## Database

The project uses SQLite with SQLAlchemy and contains:

* `users`
* `leave_requests`

Each leave request is linked to its user through `user_id`.
