# Employee Leave Management API

A RESTful Employee Leave Management API built using **FastAPI** as part of a Full Stack and Web Development assignment.

The API allows employees to register, log in securely using JWT authentication, manage their leave requests, and upload supporting documents.

## Features

- User registration with email validation
- Secure password hashing using Argon2
- JWT-based authentication
- Protected user profile endpoint
- Create, view, update, and delete leave requests
- User-specific leave authorization
- Start/end date validation
- Supporting document uploads
- File type validation for PDF, JPG, JPEG, and PNG
- SQLite database using SQLAlchemy
- Automatic API documentation with Swagger UI

## Tech Stack

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Pydantic**
- **JWT**
- **Argon2**
- **Uvicorn**

## Project Structure

```text
fastapi-learning/
│
├── main.py                 # FastAPI application and API routes
├── database.py             # Database configuration
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic validation schemas
├── security.py             # Password hashing and JWT functions
├── requirements.txt        # Python dependencies
├── leave_management.db     # SQLite database
├── uploads/                # Uploaded supporting documents
└── .gitignore