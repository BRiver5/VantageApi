from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel, ConfigDict

class Comunnity(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    community_type: Literal['Organization', 'Guild', 'Faction', 'Religion', 'Other'] | None = None


class CommunityResponse(Comunnity):
    id: UUID

    model_config = ConfigDict(from_attributes=True)