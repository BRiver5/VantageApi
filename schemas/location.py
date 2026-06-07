from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel

class Location(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    location_type: Literal['Plane', 'World', 'Continent', 'Region', 'Country', 'Village', 'City', 'Place'] | None = None
    super_location: UUID | None = None
    community_id: UUID | None = None