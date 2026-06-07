from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubRace(BaseModel):
    order: int = 0
    sub_race_name: str
    description: str | None = None
    race_features: str | None = None
    image_gallery: list[str] | None = None
    area_of_living: list[str] = Field(default_factory=list)
    increase_ability_scores: dict[str, int] = Field(default_factory=dict)
    size: str | None = None
    speed: int | None = None
    darkvision: int | None = None
    languages: list[str] | None = None
    max_age: int | None = None
    age_of_adulthood: int | None = None
    race_type: str | None = None
    flight_speed: int | None = None
    swimming_speed: int | None = None
    climbing_speed: int | None = None


class Race(BaseModel):
    race_name: str
    description: str | None = None
    race_features: str | None = None
    image_gallery: list[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    increase_ability_scores: dict[str, int] = Field(default_factory=dict)
    size: str = 'Medium'
    speed: int = 30
    darkvision: int = 0
    languages: list[str] = Field(default_factory=list)
    max_age: int = 100
    age_of_adulthood: int = 18
    race_type: str = 'humanoid'
    flight_speed: int = 0
    swimming_speed: int = 0
    climbing_speed: int = 0
    sub_races: list[SubRace] | None = None


class RaceResponse(Race):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
