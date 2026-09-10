from datetime import date
from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import User, LeaveRequest
from schemas import UserCreate, UserLogin, LeaveCreate, LeaveUpdate
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}


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


# -------------------------
# REGISTER
# -------------------------

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


# -------------------------
# LOGIN
# -------------------------

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


# -------------------------
# PROFILE
# -------------------------

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


# -------------------------
# CREATE LEAVE
# -------------------------

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


# -------------------------
# GET ALL MY LEAVES
# -------------------------

@app.get("/leaves")
def get_my_leaves(
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

    leaves = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == user.id
    ).all()

    return leaves


# -------------------------
# GET ONE LEAVE
# -------------------------

@app.get("/leaves/{leave_id}")
def get_leave(
    leave_id: int,
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

    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this leave request"
        )

    return leave


# -------------------------
# UPDATE LEAVE
# -------------------------

@app.patch("/leaves/{leave_id}")
def update_leave(
    leave_id: int,
    leave_data: LeaveUpdate,
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

    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to modify this leave request"
        )

    new_start_date = (
        leave_data.start_date
        if leave_data.start_date is not None
        else leave.start_date
    )

    new_end_date = (
        leave_data.end_date
        if leave_data.end_date is not None
        else leave.end_date
    )

    if new_end_date < new_start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    if leave_data.leave_type is not None:
        leave.leave_type = leave_data.leave_type

    if leave_data.start_date is not None:
        leave.start_date = leave_data.start_date

    if leave_data.end_date is not None:
        leave.end_date = leave_data.end_date

    if leave_data.reason is not None:
        leave.reason = leave_data.reason

    db.commit()
    db.refresh(leave)

    return {
        "message": "Leave request updated successfully",
        "leave": leave
    }


# -------------------------
# DELETE LEAVE
# -------------------------

@app.delete("/leaves/{leave_id}")
def delete_leave(
    leave_id: int,
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

    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to delete this leave request"
        )

    db.delete(leave)
    db.commit()

    return {
        "message": "Leave request deleted successfully"
    }


# -------------------------
# UPLOAD SUPPORTING DOCUMENT
# -------------------------

@app.post("/leaves/{leave_id}/document")
def upload_document(
    leave_id: int,
    file: UploadFile = File(...),
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

    leave = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found"
        )

    if leave.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to upload a document for this leave"
        )

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG, and PNG files are allowed"
        )

    file_extension = Path(file.filename).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png"
    }

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, JPG, JPEG, and PNG files are allowed"
        )

    file_name = f"leave_{leave_id}{file_extension}"
    file_path = UPLOAD_DIR / file_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    leave.supporting_document = str(file_path)

    db.commit()
    db.refresh(leave)

    return {
        "message": "Supporting document uploaded successfully",
        "file_name": file_name
    }