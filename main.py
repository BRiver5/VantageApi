from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, LargeBinary, JSON, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from schemas.spell import spell as SpellSchema, SpellResponse
from schemas.feature import class_feature as FeatureSchema, FeatureResponse
from schemas.class_resource import class_resource_template as ClassResourceSchema, ClassResourceResponse
from schemas.creatures import Creature as CreatureSchema, CreatureResponse
from schemas.character import character as CharacterSchema, CharacterResponse
from schemas.campaign import Campaign as CampaignSchema, CampaignResponse
from schemas.location import Location as LocationSchema, LocationResponse
from schemas.communities import Comunnity as CommunitySchema, CommunityResponse
from schemas.religion import Religion as ReligionSchema, ReligionResponse
from schemas.termins import Termins as TerminsSchema, TerminsResponse
from services.image_upload import save_uploaded_image
from services.crud_helpers import register_uuid_crud
from services import serializers

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
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    supported_languages = Column(JSON, default=list)
    pdf_url = Column(JSON, nullable=True)
    pages_count = Column(Integer, default=0)
    supported_versions = Column(JSON, default=list)
    new_classes = Column(ARRAY(UUID(as_uuid=True)), default=list)
    new_races = Column(ARRAY(UUID(as_uuid=True)), default=list)
    new_feats = Column(ARRAY(UUID(as_uuid=True)), default=list)
    new_items = Column(ARRAY(UUID(as_uuid=True)), default=list)
    new_spells = Column(ARRAY(UUID(as_uuid=True)), default=list)
    new_classes_count = Column(Integer, default=0)
    new_races_count = Column(Integer, default=0)
    new_feats_count = Column(Integer, default=0)
    new_items_count = Column(Integer, default=0)
    is_basic = Column(Boolean, default=False)

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
    item_source = Column(UUID(as_uuid=True), nullable=False)
    item_image_id = Column(Integer, nullable=True)
    weapon_details = Column(JSON, nullable=True)
    armor_details = Column(JSON, nullable=True)
    tool_category = Column(String, nullable=True)
    equipped_effects = Column(JSON, nullable=True)
    item_image_gallery = Column(JSON, nullable=True)


class Spell(Base):
    __tablename__ = "spells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    spell_name = Column(String, nullable=False)
    spell_level = Column(Integer, nullable=False)
    school = Column(String, nullable=False)
    casting_time = Column(String, nullable=False)
    range = Column(String, nullable=False)
    components = Column(JSON, nullable=False)
    material_components = Column(String, nullable=True)
    duration = Column(String, nullable=False)
    concentration = Column(Boolean, default=False)
    ritual = Column(Boolean, default=False)
    description = Column(String, nullable=False)
    higher_levels = Column(String, nullable=True)
    available_classes = Column(JSON, default=list)
    available_races = Column(JSON, default=list)
    available_subclasses = Column(JSON, default=list)
    spellcasting_ability = Column(String, nullable=True)
    spell_source = Column(UUID(as_uuid=True), nullable=False)


class ClassFeature(Base):
    __tablename__ = "class_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    feature_name = Column(String, nullable=False)
    feature_source = Column(UUID(as_uuid=True), nullable=False)
    class_source = Column(UUID(as_uuid=True), nullable=False)
    level_required = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="standard")
    resource_key = Column(String, nullable=True)
    is_optional = Column(Boolean, default=False)
    effects = Column(JSON, default=list)
    options = Column(JSON, nullable=True)
    prerequisite_features = Column(JSON, default=list)


class ClassResource(Base):
    __tablename__ = "class_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    resource_key = Column(String, nullable=False)
    resource_name = Column(String, nullable=False)
    class_source = Column(UUID(as_uuid=True), nullable=False)
    kind = Column(String, nullable=False)
    description = Column(String, nullable=False)
    recharge = Column(String, nullable=True)
    level_scaling = Column(JSON, nullable=True)
    collection_catalog = Column(JSON, default=list)
    collection_size_scaling = Column(JSON, nullable=True)
    activation_effects = Column(JSON, default=list)
    passive_effects = Column(JSON, default=list)
    level_required = Column(Integer, default=1)


class Creature(Base):
    __tablename__ = "creatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    is_npc = Column(Boolean, default=False)
    community_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String, nullable=False)
    is_unique = Column(Boolean, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(JSON, nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)
    size = Column(String, nullable=True)
    creature_type = Column(String, nullable=True)
    alignment = Column(String, nullable=True)
    ac = Column(Integer, nullable=False)
    ac_source = Column(String, nullable=True)
    hp = Column(Integer, nullable=False)
    hp_formula = Column(String, nullable=True)
    speed = Column(Integer, nullable=True)
    flight_speed = Column(Integer, nullable=True)
    swim_speed = Column(Integer, nullable=True)
    burrow_speed = Column(Integer, nullable=True)
    climb_speed = Column(Integer, nullable=True)
    strenght = Column(Integer, nullable=True)
    dexterity = Column(Integer, nullable=True)
    constitution = Column(Integer, nullable=True)
    intelligence = Column(Integer, nullable=True)
    wisdom = Column(Integer, nullable=True)
    charisma = Column(Integer, nullable=True)
    saving_throws = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    damage_imunities = Column(JSON, nullable=True)
    damage_resistances = Column(JSON, nullable=True)
    damage_vulnerabilities = Column(JSON, nullable=True)
    condition_imunities = Column(JSON, nullable=True)
    night_vision = Column(Integer, nullable=True)
    blind_vision = Column(Integer, nullable=True)
    true_vision = Column(Integer, nullable=True)
    languages = Column(JSON, nullable=True)
    can_speak = Column(Boolean, nullable=True)
    challenge_rating = Column(Float, nullable=True)
    proficiency_bonus = Column(Integer, nullable=True)
    area_of_living = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    actions_description = Column(String, nullable=True)
    legendary_actions = Column(JSON, nullable=True)
    legendary_description = Column(String, nullable=True)
    mythical_actions = Column(JSON, nullable=True)
    mythical_description = Column(String, nullable=True)
    creature_description = Column(String, nullable=True)
    image_gallery = Column(JSON, nullable=True)


class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    player_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    character_name = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_gallery = Column(JSON, nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)
    campaign_type = Column(String, nullable=True)
    campaign_lenght = Column(String, nullable=True)
    campaign_setting = Column(String, nullable=True)
    preferable_system = Column(String, nullable=True)
    preferable_player_count = Column(Integer, nullable=True)
    preferable_player_minimum_level = Column(Integer, nullable=True)
    preferable_player_maximum_level = Column(Integer, nullable=True)
    chapters = Column(JSON, nullable=True)
    custom_creatures = Column(JSON, nullable=True)
    custom_locations = Column(JSON, nullable=True)
    custom_communities = Column(JSON, nullable=True)


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_gallery = Column(JSON, nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)
    location_type = Column(String, nullable=True)
    super_location = Column(UUID(as_uuid=True), nullable=True)
    community_id = Column(UUID(as_uuid=True), nullable=True)


class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_gallery = Column(JSON, nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)
    community_type = Column(String, nullable=True)


class Religion(Base):
    __tablename__ = "religions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_gallery = Column(JSON, nullable=True)
    settings_id = Column(UUID(as_uuid=True), nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)


class Termins(Base):
    __tablename__ = "termins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_gallery = Column(JSON, nullable=True)
    book_source_id = Column(UUID(as_uuid=True), nullable=True)

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


def ensure_schema() -> None:
    """Приводит схему PostgreSQL в соответствие с ORM-моделями."""
    migrations = [
        # books: legacy book_cover_url → book_cover_image_id
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'books'
                  AND column_name = 'book_cover_url'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'books'
                  AND column_name = 'book_cover_image_id'
            ) THEN
                ALTER TABLE books DROP COLUMN book_cover_url;
            END IF;
        END $$;
        """,
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS book_cover_image_id INTEGER;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS settings_id UUID;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS is_basic BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS supported_languages JSON DEFAULT '[]'::json;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS pdf_url JSON;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS pages_count INTEGER DEFAULT 0;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS supported_versions JSON DEFAULT '[]'::json;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_classes UUID[] DEFAULT '{}';",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_races UUID[] DEFAULT '{}';",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_feats UUID[] DEFAULT '{}';",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_items UUID[] DEFAULT '{}';",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_spells UUID[] DEFAULT '{}';",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_classes_count INTEGER DEFAULT 0;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_races_count INTEGER DEFAULT 0;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_feats_count INTEGER DEFAULT 0;",
        "ALTER TABLE books ADD COLUMN IF NOT EXISTS new_items_count INTEGER DEFAULT 0;",
        "ALTER TABLE items ADD COLUMN IF NOT EXISTS item_image_id INTEGER;",
        "ALTER TABLE items ADD COLUMN IF NOT EXISTS equipped_effects JSON;",
        "ALTER TABLE items ADD COLUMN IF NOT EXISTS tool_category VARCHAR;",
        "ALTER TABLE items ADD COLUMN IF NOT EXISTS item_image_gallery JSON;",
    ]
    try:
        with engine.begin() as conn:
            for migration in migrations:
                conn.execute(text(migration))
        logger.info("Database schema migration completed")
    except Exception:
        logger.exception("Database schema migration failed")


ensure_schema()

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
        supported_languages=book.supported_languages or [],
        pdf_url=book.pdf_url,
        pages_count=book.pages_count or 0,
        supported_versions=book.supported_versions or [],
        new_classes=book.new_classes or [],
        new_races=book.new_races or [],
        new_feats=book.new_feats or [],
        new_items=book.new_items or [],
        new_spells=book.new_spells or [],
        new_classes_count=book.new_classes_count or 0,
        new_races_count=book.new_races_count or 0,
        new_feats_count=book.new_feats_count or 0,
        new_items_count=book.new_items_count or 0,
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
        tool_category=db_item.tool_category,
        equipped_effects=db_item.equipped_effects or [],
        item_image_gallery=db_item.item_image_gallery,
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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

    db_item = Item(**serializers.item_schema_to_orm(item_data, item_image_id))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return build_item_response(db, db_item)

# Get all items
@app.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return [build_item_response(db, item) for item in items]


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: PyUUID, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return build_item_response(db, db_item)


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: PyUUID,
    item_json: str = Form(..., description="JSON с полями предмета (schemas.item)"),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = ItemSchema.model_validate_json(item_json)
    update_data = serializers.item_schema_to_orm(item_data, db_item.item_image_id)
    if image is not None:
        update_data["item_image_id"] = await save_uploaded_image(image, db, CloudImage)

    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return build_item_response(db, db_item)


@app.delete("/items/{item_id}")
def delete_item(item_id: PyUUID, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"deleted": item_id}


# Update a book
@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: PyUUID,
    title: str = Form(...),
    book_code: str = Form(...),
    author: str = Form(...),
    published_date: str = Form(...),
    is_basic: bool = Form(False),
    pages_count: int = Form(0),
    campaign_id: str | None = Form(None),
    settings_id: str | None = Form(None),
    supported_languages: str = Form("[]"),
    supported_versions: str = Form("[]"),
    cover: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = title
    book.book_code = book_code
    book.author = author
    book.published_date = parse_datetime(published_date)
    book.is_basic = is_basic
    book.pages_count = pages_count
    book.campaign_id = parse_optional_uuid(campaign_id)
    book.settings_id = parse_optional_uuid(settings_id)
    book.supported_languages = json.loads(supported_languages)
    book.supported_versions = json.loads(supported_versions)
    if cover is not None:
        book.book_cover_image_id = await save_uploaded_image(cover, db, CloudImage)

    db.commit()
    db.refresh(book)
    return build_book_response(db, book)


@app.delete("/books/{book_id}")
def delete_book(book_id: PyUUID, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"deleted": book_id}


CRUD_ENTITIES = [
    ("/spells", "Spell", Spell, SpellSchema, SpellResponse, serializers.spell_to_orm, serializers.spell_to_response),
    ("/features", "ClassFeature", ClassFeature, FeatureSchema, FeatureResponse, serializers.feature_to_orm, serializers.feature_to_response),
    ("/class-resources", "ClassResource", ClassResource, ClassResourceSchema, ClassResourceResponse, serializers.class_resource_to_orm, serializers.class_resource_to_response),
    ("/creatures", "Creature", Creature, CreatureSchema, CreatureResponse, serializers.creature_to_orm, serializers.creature_to_response),
    ("/characters", "Character", Character, CharacterSchema, CharacterResponse, serializers.character_to_orm, serializers.character_to_response),
    ("/campaigns", "Campaign", Campaign, CampaignSchema, CampaignResponse, serializers.campaign_to_orm, serializers.campaign_to_response),
    ("/locations", "Location", Location, LocationSchema, LocationResponse, serializers.location_to_orm, serializers.location_to_response),
    ("/communities", "Community", Community, CommunitySchema, CommunityResponse, serializers.community_to_orm, serializers.community_to_response),
    ("/religions", "Religion", Religion, ReligionSchema, ReligionResponse, serializers.religion_to_orm, serializers.religion_to_response),
    ("/termins", "Termins", Termins, TerminsSchema, TerminsResponse, serializers.termins_to_orm, serializers.termins_to_response),
]

for prefix, tag, orm_model, create_schema, response_schema, to_orm, to_response in CRUD_ENTITIES:
    app.include_router(
        register_uuid_crud(
            prefix=prefix,
            tag=tag,
            orm_model=orm_model,
            create_schema=create_schema,
            response_schema=response_schema,
            to_orm=to_orm,
            to_response=to_response,
            get_db=get_db,
        )
    )