from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GameClass(BaseModel):
    class_name: str
    description: str | None = None
    image_gallery: list[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    hit_dice: int
    saving_throw_proficiencies: list[str] = Field(default_factory=list)
    armor_proficiencies: list[str] = Field(default_factory=list)
    weapon_proficiencies: list[str] = Field(default_factory=list)
    speed_bonus: int = 0
    is_caster: bool = False
    default_spellcasting_ability: str | None = None
    class_resource_keys: list[str] = Field(default_factory=list)


class GameClassResponse(GameClass):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
