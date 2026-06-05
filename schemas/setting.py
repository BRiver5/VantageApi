from uuid import UUID

from pydantic import BaseModel


class SettingResponse(BaseModel):
    id: UUID
    settings_title: str
    settings_description: str
    settings_picture_ids: list[int]
    settings_picture_urls: list[str | None]

    class Config:
        from_attributes = True
