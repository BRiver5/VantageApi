from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, LargeBinary, JSON, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os
from uuid import UUID as PyUUID, uuid4
import cloudinary
import cloudinary.uploader
import logging

from schemas.item import item as ItemSchema
from schemas.book import BookResponse
from schemas.setting import SettingResponse
from schemas.item_response import ItemResponse
from services.image_upload import save_uploaded_image

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
    secure=True
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    favourite_settings = Column(ARRAY(UUID(as_uuid=True)))  # List of favourite setting IDs

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)

class CampaignSettings(Base):
    __tablename__ = "campaign_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    settings_pictures = Column(String)  # JSON-массив ID изображений из cloud_images
    settings_title = Column(String)
    settings_description = Column(String)
    likes = Column(Integer, default=0)
    
class Books(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String, nullable=False)
    book_cover_image_id = Column(Integer, nullable=True)
    book_code = Column(String, unique=True, nullable=False)
    author = Column(String, nullable=False)
    published_date = Column(DateTime, nullable=False)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)  # ID кампании, к которой относится книга
    settings_id = Column(UUID(as_uuid=True), nullable=True)  # ID сэттингов кампании, к которой относится книга
    is_basic = Column(Boolean, default=False)  # True если базовая книга, False если пользовательская

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    item_name = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    attunement_required = Column(Boolean, nullable=False)
    weight = Column(Float, nullable=False)
    cost_copper = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    item_source = Column(UUID(as_uuid=True), nullable=False)  # ID книги, из которой взят предмет
    item_image_id = Column(Integer, nullable=True)
    weapon_details = Column(JSON, nullable=True)  # Хранит JSON объект
    armor_details = Column(JSON, nullable=True)   # Хранит JSON объект
    equipped_effects = Column(JSON, nullable=True)
    

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

class CloudImage(Base):
    __tablename__ = "cloud_images"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    public_id = Column(String)


# Создаёт таблицы если их нет
Base.metadata.create_all(engine)

# --- Dependency для сессии ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_image_url(db: Session, image_id: int | None) -> str | None:
    if image_id is None:
        return None
    image = db.query(CloudImage).filter(CloudImage.id == image_id).first()
    return image.url if image else None


def parse_picture_ids(raw: str | None) -> list[int]:
    if not raw:
        return []
    return json.loads(raw)


def build_book_response(db: Session, book: Books) -> BookResponse:
    return BookResponse(
        id=book.id,
        title=book.title,
        book_cover_image_id=book.book_cover_image_id,
        book_cover_url=get_image_url(db, book.book_cover_image_id),
        book_code=book.book_code,
        author=book.author,
        published_date=book.published_date,
        campaign_id=book.campaign_id,
        settings_id=book.settings_id,
        is_basic=book.is_basic,
    )


def build_setting_response(db: Session, setting: CampaignSettings) -> SettingResponse:
    picture_ids = parse_picture_ids(setting.settings_pictures)
    return SettingResponse(
        id=setting.id,
        settings_title=setting.settings_title,
        settings_description=setting.settings_description,
        settings_picture_ids=picture_ids,
        settings_picture_urls=[get_image_url(db, image_id) for image_id in picture_ids],
    )


def build_item_response(db: Session, db_item: Item) -> ItemResponse:
    return ItemResponse(
        id=db_item.id,
        item_name=db_item.item_name,
        item_type=db_item.item_type,
        rarity=db_item.rarity,
        attunement_required=db_item.attunement_required,
        weight=db_item.weight,
        cost_copper=db_item.cost_copper,
        description=db_item.description,
        item_source=db_item.item_source,
        item_image_id=db_item.item_image_id,
        item_image_url=get_image_url(db, db_item.item_image_id),
        weapon_details=db_item.weapon_details,
        armor_details=db_item.armor_details,
        equipped_effects=db_item.equipped_effects or [],
    )


def parse_optional_uuid(value: str | None) -> PyUUID | None:
    if not value:
        return None
    return PyUUID(value)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


app = FastAPI()

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://vantagedevui.vercel.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
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
@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        image_id = await save_uploaded_image(file, db, CloudImage)
        db.commit()
        image = db.query(CloudImage).filter(CloudImage.id == image_id).first()
        return {
            "id": image.id,
            "url": image.url,
            "public_id": image.public_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Get image by database ID
@app.get("/images/{image_id}")
def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    image = db.query(CloudImage).filter(CloudImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "id": image.id,
        "url": image.url,
        "public_id": image.public_id,
    }

# Get image by public_id
@app.get("/images/public/{public_id}")
def get_image(public_id: str, db: Session = Depends(get_db)):
    image = db.query(CloudImage).filter(CloudImage.public_id == public_id).first()
    print(public_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return {
        "id": image.id,
        "url": image.url,
        "public_id": image.public_id,
    }

# Delete an image by public_id
@app.delete("/images/{public_id}")
def delete_image(public_id: str, db: Session = Depends(get_db)):
    image = db.query(CloudImage).filter(CloudImage.public_id == public_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    destroy_result = cloudinary.uploader.destroy(public_id)
    if destroy_result.get("result") != "ok":
        raise HTTPException(status_code=404, detail="Image not found in cloud storage")

    db.delete(image)
    db.commit()

    return {"deleted": public_id}

# Get all books
@app.get("/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Books).all()
    return [build_book_response(db, book) for book in books]

# Get a book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: PyUUID, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return build_book_response(db, book)

# Create a book
@app.post("/books", response_model=BookResponse)
async def create_book(
    title: str = Form(...),
    book_code: str = Form(...),
    author: str = Form(...),
    published_date: str = Form(...),
    is_basic: bool = Form(False),
    campaign_id: str | None = Form(None),
    settings_id: str | None = Form(None),
    cover: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    cover_image_id = await save_uploaded_image(cover, db, CloudImage)
    db_book = Books(
        title=title,
        book_cover_image_id=cover_image_id,
        book_code=book_code,
        author=author,
        published_date=parse_datetime(published_date),
        campaign_id=parse_optional_uuid(campaign_id),
        settings_id=parse_optional_uuid(settings_id),
        is_basic=is_basic,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return build_book_response(db, db_book)

# Add a setting
@app.post("/settings", response_model=SettingResponse)
async def add_setting(
    settings_title: str = Form(...),
    settings_description: str = Form(...),
    pictures: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    if not pictures:
        raise HTTPException(status_code=400, detail="At least one picture is required")

    picture_ids = []
    for picture in pictures:
        picture_ids.append(await save_uploaded_image(picture, db, CloudImage))

    db_setting = CampaignSettings(
        settings_title=settings_title,
        settings_description=settings_description,
        settings_pictures=json.dumps(picture_ids),
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return build_setting_response(db, db_setting)

# Get all settings
@app.get("/settings", response_model=list[SettingResponse])
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(CampaignSettings).all()
    return [build_setting_response(db, setting) for setting in settings]

# Get a setting by ID
@app.get("/settings/{setting_id}", response_model=SettingResponse)
def get_setting(setting_id: PyUUID, db: Session = Depends(get_db)):
    setting = db.query(CampaignSettings).filter(CampaignSettings.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return build_setting_response(db, setting)

# Update a setting
@app.put("/settings/{setting_id}", response_model=SettingResponse)
def update_setting(
    setting_id: PyUUID,
    settings_title: str = Form(...),
    settings_description: str = Form(...),
    db: Session = Depends(get_db),
):
    setting = db.query(CampaignSettings).filter(CampaignSettings.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.settings_title = settings_title
    setting.settings_description = settings_description
    db.commit()
    db.refresh(setting)
    return build_setting_response(db, setting)

# Delete a setting
@app.delete("/settings/{setting_id}")
def delete_setting(setting_id: PyUUID, db: Session = Depends(get_db)):
    setting = db.query(CampaignSettings).filter(CampaignSettings.id == setting_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"deleted": setting_id}

# Add an item
@app.post("/items", response_model=ItemResponse)
async def add_item(
    item_json: str = Form(..., description="JSON с полями предмета (schemas.item)"),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    item_data = ItemSchema.model_validate_json(item_json)
    item_image_id = None
    if image is not None:
        item_image_id = await save_uploaded_image(image, db, CloudImage)

    db_item = Item(
        item_name=item_data.item_name,
        item_type=item_data.item_type,
        rarity=item_data.rarity,
        attunement_required=item_data.attunement_required,
        weight=item_data.weight,
        cost_copper=item_data.cost_copper,
        description=item_data.description,
        item_source=item_data.item_source,
        item_image_id=item_image_id,
        weapon_details=item_data.weapon.model_dump() if item_data.weapon else None,
        armor_details=item_data.armor.model_dump() if item_data.armor else None,
        equipped_effects=[effect.model_dump() for effect in item_data.equipped_effects],
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return build_item_response(db, db_item)

# Get all items
@app.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return [build_item_response(db, item) for item in items]