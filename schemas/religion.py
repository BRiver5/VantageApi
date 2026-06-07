from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel

class Religion(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None