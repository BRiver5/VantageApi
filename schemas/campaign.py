from __future__ import annotations

from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


class Dungeon_fill(BaseModel):
    treasures: List[UUID] | None = None
    traps: List[UUID] | None = None
    enemies: List[UUID] | None = None
    coins: int | None = None


class Room(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    text_content: str
    fill: Dungeon_fill | None = None


class Dungeon(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    text_content: str
    rooms: List[Room] | None = None
    fill: Dungeon_fill | None = None


class Chapter(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    text_content: str
    fill: Dungeon_fill | None = None


class Campaign(BaseModel):
    name: str
    description: str | None = None
    image_gallery: List[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None

    campaign_type: Literal['Homebrew', 'Published', 'Other'] | None = None
    campaign_lenght: Literal['One-shot', 'Adventure', 'Mini-Campaign', 'Module'] | None = None
    campaign_setting: Literal['Fantasy', 'Sci-fi', 'Horror', 'Post-apocalyptic', 'Other'] | None = None

    preferable_system: str | None = None
    preferable_player_count: int | None = None
    preferable_player_minimum_level: int | None = None
    preferable_player_maximum_level: int | None = None

    chapters: List[Chapter] | None = None

    custom_creatures: List[UUID] | None = None
    custom_locations: List[UUID] | None = None
    custom_communities: List[UUID] | None = None


class CampaignResponse(Campaign):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
