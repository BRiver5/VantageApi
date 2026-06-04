from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, LargeBinary, String
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import UUID
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
import os
from uuid import uuid4
from schemas.character import character

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    USER = os.getenv("user") or os.getenv("USER")
    PASSWORD = os.getenv("password") or os.getenv("PASSWORD")
    HOST = os.getenv("host") or os.getenv("HOST")
    PORT = os.getenv("port") or os.getenv("PORT")
    DBNAME = os.getenv("dbname") or os.getenv("DBNAME")
    DB_SSLMODE = os.getenv("DB_SSLMODE")
    if USER and PASSWORD and HOST and PORT and DBNAME:
        DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
        if DB_SSLMODE:
            DATABASE_URL += f"?sslmode={DB_SSLMODE}"
    else:
        raise RuntimeError(
            "Database URL is not set. Set DATABASE_URL or USER/PASSWORD/HOST/PORT/DBNAME."
        )

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Create the SQLAlchemy engine
# Using the Transaction Pooler, so we disable SQLAlchemy client side pooling
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)

# Создаёт таблицы если их нет
Base.metadata.create_all(engine)

# --- Pydantic схемы ---

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Dependency для сессии ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "running"}

# Get all users
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Create a user
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Update a user
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = data.name
    user.email = data.email
    db.commit()
    db.refresh(user)
    return user

# Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"deleted": user_id}

# Upload an image
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    image = Image(
        filename=file.filename,
        content_type=file.content_type,
        data=content,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"id": image.id}

# Get an image by ID
@app.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return {
        "filename": image.filename,
        "content_type": image.content_type,
        "data": image.data,
    }

# Delete an image by ID
@app.delete("/images/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(image)
    db.commit()
    return {"deleted": image_id}