from uuid import UUID
from typing import List

from pydantic import BaseModel, ConfigDict

class Termins(BaseModel):
    name: str
    description: str
    image_gallery: List[str] | None = None
    book_source_id: UUID | None = None


class TerminsResponse(Termins):
    id: UUID

    model_config = ConfigDict(from_attributes=True)