from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BookResponse(BaseModel):
    id: UUID
    title: str
    book_cover_image_id: int | None = None
    book_cover_url: str | None = None
    book_code: str
    author: str
    published_date: datetime
    campaign_id: UUID | None = None
    settings_id: UUID | None = None
    supported_languages: list[Literal["en", "ru"]]
    pdf_url: list[str] | None = None
    pages_count: int
    supported_versions: list[Literal["5e", "3.5e", "3e", "2e", "1e", "dnd beyond", "advanced dnd"]]
    new_classes: list[UUID]
    new_races: list[UUID]
    new_feats: list[UUID]
    new_items: list[UUID]
    new_spells: list[UUID]
    new_classes_count: int
    new_races_count: int
    new_feats_count: int
    new_items_count: int
    is_basic: bool

    model_config = ConfigDict(from_attributes=True)