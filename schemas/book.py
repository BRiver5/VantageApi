from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
    is_basic: bool

    class Config:
        from_attributes = True