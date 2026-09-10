from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import User, LeaveRequest
from schemas import UserCreate, UserLogin, LeaveCreate
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    email = verify_token(token)

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return email


@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {"sub": existing_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/profile")
def profile(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_active": user.is_active
    }

@app.post("/leaves")
def create_leave(
    leave: LeaveCreate,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if leave.end_date < leave.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    new_leave = LeaveRequest(
        user_id=user.id,
        leave_type=leave.leave_type,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason
    )

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return {
        "message": "Leave request submitted successfully",
        "leave_id": new_leave.id
    }