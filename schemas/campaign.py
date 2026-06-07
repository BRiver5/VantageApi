from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Dungeon_fill(BaseModel):
    treasures: list[UUID] | None = None
    traps: list[UUID] | None = None
    enemies: list[UUID] | None = None
    coins: int | None = None


class Room(BaseModel):
    order: int = 0
    name: str
    description: str | None = None
    image_gallery: list[str] | None = None
    text_content: str
    fill: Dungeon_fill | None = None


class Dungeon(BaseModel):
    name: str
    description: str | None = None
    image_gallery: list[str] | None = None
    text_content: str
    rooms: list[Room] | None = None
    fill: Dungeon_fill | None = None


class Chapter(BaseModel):
    name: str
    description: str | None = None
    image_gallery: list[str] | None = None
    text_content: str
    fill: Dungeon_fill | None = None


class CampaignContentBlock(BaseModel):
    order: int = 0
    kind: Literal["chapter", "dungeon"]
    chapter: Chapter | None = None
    dungeon: Dungeon | None = None


class Campaign(BaseModel):
    name: str
    description: str | None = None
    image_gallery: list[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    order: int | None = None

    campaign_type: Literal['Homebrew', 'Published', 'Other'] | None = None
    campaign_lenght: Literal['One-shot', 'Adventure', 'Mini-Campaign', 'Module'] | None = None
    campaign_setting: Literal['Fantasy', 'Sci-fi', 'Horror', 'Post-apocalyptic', 'Other'] | None = None

    preferable_system: str | None = None
    preferable_player_count: int | None = None
    preferable_player_minimum_level: int | None = None
    preferable_player_maximum_level: int | None = None

    content: list[CampaignContentBlock] | None = None
    chapters: list[Chapter] | None = Field(default=None, deprecated=True)

    custom_creatures: list[UUID] | None = None
    custom_locations: list[UUID] | None = None
    custom_communities: list[UUID] | None = None


class CampaignResponse(Campaign):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
